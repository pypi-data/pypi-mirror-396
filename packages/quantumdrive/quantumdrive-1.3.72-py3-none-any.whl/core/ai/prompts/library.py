import logging
from typing import Optional, Any
from jinja2 import Template
from .partials import PromptPartials

logger = logging.getLogger(__name__)

class PromptLibrary:
    """
    Central repository for building and retrieving composed prompts.
    """

    @staticmethod
    def compile_template(template_str: str, **kwargs: Any) -> str:
        """Helper to render a Jinja2 template string."""
        template = Template(template_str)
        return template.render(**kwargs)

    @staticmethod
    def build_system_prompt(
        base_role: str = PromptPartials.DEFAULT_SYSTEM_ROLE,
        include_thought_process: bool = False,
        json_schema: Optional[str] = None
    ) -> str:
        """
        Constructs a full system prompt from modular parts.
        Legacy method; use build() for more control.
        """
        parts = [base_role]

        if include_thought_process:
            parts.append(PromptPartials.THOUGHT_PROCESS)

        if json_schema:
            # Reconstruct the logic using OUTPUT_CONSTRAINTS for backward compat
            # or simply append the old style instruction if we kept it.
            # Here we will redirect to the new way implicitly.
            json_instr = PromptLibrary.compile_template(
                PromptPartials.OUTPUT_CONSTRAINTS,
                format_type="JSON",
                schema=json_schema
            )
            parts.append(json_instr)

        return "\n\n".join(parts)
    
    @staticmethod
    def build(
        role: str = PromptPartials.DEFAULT_SYSTEM_ROLE,
        instruction: str = "",
        context: str = "",
        examples: Optional[str] = None,
        reasoning_pattern: Optional[str] = None,
        output_format: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Advanced prompt builder supporting all patterns.
        
        Args:
            role: The system persona (default: Q).
            instruction: The core task instruction.
            context: Additional context for the task.
            examples: Few-shot examples string (injected into FEW_SHOT template).
            reasoning_pattern: e.g., PromptPartials.CHAIN_OF_THOUGHT or PromptPartials.REFLECTION.
            output_format: e.g. "JSON", "MARKDOWN". Use kwargs['schema'] for JSON.
            **kwargs: Additional variables for templates (e.g. 'schema' for JSON).
        """
        logger.debug(
            "Building prompt: role='%s' instruction_len=%d context_len=%d examples=%s reasoning=%s output=%s kwargs=%s",
            role.split('\n')[0] if role else "None", 
            len(instruction), 
            len(context), 
            "Yes" if examples else "No", 
            "Yes" if reasoning_pattern else "No", 
            output_format,
            kwargs.keys()
        )

        parts = [role]
        
        if context:
            parts.append(f"### CONTEXT\n{context}")
            
        if instruction:
            parts.append(f"### INSTRUCTION\n{instruction}")
            
        if examples:
            parts.append(PromptLibrary.compile_template(PromptPartials.FEW_SHOT, examples=examples))
            
        if reasoning_pattern:
            parts.append(reasoning_pattern)
            
        if output_format:
            # If output_constraints template is used
            schema = kwargs.get('schema', '')
            additional = kwargs.get('additional_constraints', '')
            parts.append(PromptLibrary.compile_template(
                PromptPartials.OUTPUT_CONSTRAINTS, 
                format_type=output_format,
                schema=schema,
                additional_constraints=additional
            ))
            
        result = "\n\n".join(parts)
        logger.info("Prompt built successfully. Total length: %d chars", len(result))
        return result
