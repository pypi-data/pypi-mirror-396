import json
import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

from .llm_execution_result import LLMExecutionResult

logger = logging.getLogger(__name__)


class LLMDSLExecutor:
    """
    LLM-driven DSL executor.
    
    NO HARDCODED:
    - Task type keywords
    - Field mappings
    - Filter patterns
    
    Everything inferred by LLM from context.
    """
    
    def __init__(self, page=None, llm=None, run_logger=None):
        self.page = page
        self.llm = llm
        self.run_logger = run_logger
    
    async def execute(
        self,
        instruction: str,
        url: Optional[str] = None
    ) -> LLMExecutionResult:
        """Execute DSL strategy using LLM inference."""
        start_time = time.time()
        self._log("🔧 LLM DSL EXECUTOR", "header")
        
        if not self.llm:
            return LLMExecutionResult(
                success=False, data=None, task_type='unknown',
                algorithm_used='none', execution_time_ms=0,
                fields_detected=[], filter_expr=None
            )
        
        try:
            # Get URL if not provided
            if not url and self.page:
                url = await self.page.evaluate("() => location.href")
            
            # Phase 1: LLM detects task type
            task_type = await self._detect_task_type_llm(instruction)
            self._log(f"Task type: {task_type}")
            
            # Phase 2: LLM infers required fields
            fields = await self._detect_fields_llm(instruction, task_type)
            self._log(f"Fields: {fields}")
            
            # Phase 3: LLM parses filter expression
            filter_expr = await self._detect_filter_llm(instruction)
            if filter_expr:
                self._log(f"Filter: {filter_expr}")
            
            # Phase 4: Select and execute algorithm
            algorithm = await self._select_algorithm_llm(task_type, instruction)
            self._log(f"Algorithm: {algorithm}")
            
            data = await self._execute_algorithm(algorithm, fields, filter_expr)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            return LLMExecutionResult(
                success=data is not None,
                data=data,
                task_type=task_type,
                algorithm_used=algorithm,
                execution_time_ms=execution_time_ms,
                fields_detected=fields,
                filter_expr=filter_expr
            )
            
        except Exception as e:
            self._log(f"Error: {e}", "error")
            return LLMExecutionResult(
                success=False, data=None, task_type='error',
                algorithm_used='none',
                execution_time_ms=int((time.time() - start_time) * 1000),
                fields_detected=[], filter_expr=None
            )
    
    async def _detect_task_type_llm(self, instruction: str) -> str:
        """Detect task type using LLM."""
        prompt = f"""Classify this web automation instruction into one task type.

Instruction: "{instruction}"

Task types:
- extract_products: extracting product listings with prices
- extract_specs: extracting technical specifications
- extract_links: extracting URLs/links
- extract_contacts: extracting email/phone/address
- fill_form: filling out a form
- screenshot: taking a screenshot
- extract: generic data extraction

Return ONLY the task type, nothing else."""

        try:
            response = await self.llm.agenerate([prompt])
            answer = response.generations[0][0].text.strip().lower()
            
            valid_types = [
                'extract_products', 'extract_specs', 'extract_links',
                'extract_contacts', 'fill_form', 'screenshot', 'extract'
            ]
            
            for t in valid_types:
                if t in answer:
                    return t
            
            return 'extract'
        except Exception:
            return 'extract'
    
    async def _detect_fields_llm(
        self, 
        instruction: str, 
        task_type: str
    ) -> List[str]:
        """Detect required fields using LLM."""
        prompt = f"""What data fields should be extracted for this task?

Instruction: "{instruction}"
Task type: {task_type}

Return JSON array of field names:
["name", "price", "url", ...]

Return ONLY the JSON array."""

        try:
            response = await self.llm.agenerate([prompt])
            answer = response.generations[0][0].text.strip()
            
            import re
            if '```' in answer:
                answer = re.sub(r'```\w*\n?', '', answer)
            
            fields = json.loads(answer)
            return fields if isinstance(fields, list) else []
        except Exception:
            # Reasonable defaults based on task
            defaults = {
                'extract_products': ['name', 'price', 'url'],
                'extract_specs': ['key', 'value'],
                'extract_links': ['text', 'url'],
                'extract_contacts': ['name', 'email', 'phone'],
            }
            return defaults.get(task_type, ['name', 'url'])
    
    async def _detect_filter_llm(self, instruction: str) -> Optional[str]:
        """Detect filter expression using LLM."""
        prompt = f"""Does this instruction contain a filter condition (e.g., price limit)?

Instruction: "{instruction}"

If yes, return the filter as a simple expression like "price < 100" or "price > 50".
If no filter, return "none".

Return ONLY the filter expression or "none"."""

        try:
            response = await self.llm.agenerate([prompt])
            answer = response.generations[0][0].text.strip().lower()
            
            if answer == 'none' or 'none' in answer:
                return None
            
            # Clean up the response
            answer = answer.replace('"', '').replace("'", '')
            if '<' in answer or '>' in answer:
                return answer
            
            return None
        except Exception:
            return None
    
    async def _select_algorithm_llm(
        self, 
        task_type: str, 
        instruction: str
    ) -> str:
        """Select best algorithm using LLM."""
        prompt = f"""Select the best extraction algorithm for this task.

Task type: {task_type}
Instruction: "{instruction}"

Algorithms:
- statistical: find repeating patterns statistically
- llm_guided: use LLM to identify elements
- table: extract from HTML tables
- links: extract anchor elements

Return ONLY the algorithm name."""

        try:
            response = await self.llm.agenerate([prompt])
            answer = response.generations[0][0].text.strip().lower()
            
            if 'table' in answer:
                return 'table'
            elif 'link' in answer:
                return 'links'
            elif 'statistical' in answer or 'pattern' in answer:
                return 'statistical'
            else:
                return 'llm_guided'
        except Exception:
            return 'llm_guided'
    
    async def _execute_algorithm(
        self,
        algorithm: str,
        fields: List[str],
        filter_expr: Optional[str]
    ) -> Optional[Any]:
        """Execute the selected algorithm."""
        if not self.page:
            return None
        
        try:
            if algorithm == 'table':
                return await self._extract_tables(fields)
            elif algorithm == 'links':
                return await self._extract_links(fields)
            elif algorithm == 'statistical':
                return await self._extract_statistical(fields)
            else:
                return await self._extract_llm_guided(fields)
        except Exception as e:
            self._log(f"Algorithm failed: {e}", "error")
            return None
    
    async def _extract_tables(self, fields: List[str]) -> List[Dict]:
        """Extract data from tables."""
        return await self.page.evaluate("""() => {
            const tables = document.querySelectorAll('table');
            const results = [];
            
            tables.forEach(table => {
                const rows = table.querySelectorAll('tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td, th');
                    if (cells.length >= 2) {
                        results.push({
                            key: cells[0]?.textContent?.trim() || '',
                            value: cells[1]?.textContent?.trim() || ''
                        });
                    }
                });
            });
            
            return results.filter(r => r.key || r.value);
        }""")
    
    async def _extract_links(self, fields: List[str]) -> List[Dict]:
        """Extract links from page."""
        return await self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a[href]'))
                .map(a => ({
                    text: a.textContent?.trim() || '',
                    url: a.href
                }))
                .filter(l => l.text && l.url);
        }""")
    
    async def _extract_statistical(self, fields: List[str]) -> List[Dict]:
        """Extract using statistical pattern detection."""
        # Use DOM toolkit if available
        try:
            from curllm_core.llm_dsl import AtomicFunctions
            atoms = AtomicFunctions(page=self.page, llm=self.llm)
            result = await atoms.find_repeating_pattern()
            if result.success:
                return result.data.get('items', [])
        except Exception:
            pass
        
        # Fallback: find common container patterns
        return await self.page.evaluate("""() => {
            // Find elements with similar structure
            const containers = document.querySelectorAll('[class*="item"], [class*="product"], [class*="card"]');
            return Array.from(containers).slice(0, 20).map(el => ({
                text: el.textContent?.trim().substring(0, 200) || '',
                html: el.outerHTML.substring(0, 500)
            }));
        }""")
    
    async def _extract_llm_guided(self, fields: List[str]) -> Optional[Any]:
        """Extract using LLM guidance."""
        try:
            from curllm_core.llm_dsl import AtomicFunctions
            atoms = AtomicFunctions(page=self.page, llm=self.llm)
            
            result = await atoms.extract_data_pattern(
                f"extract {', '.join(fields)} from the page"
            )
            
            if result.success:
                return result.data
        except Exception:
            pass
        
        return None
    
    def _log(self, message: str, level: str = "info"):
        """Log message."""
        if self.run_logger:
            if level == "header":
                self.run_logger.log_text(f"\n{'='*50}\n{message}\n{'='*50}")
            elif level == "error":
                self.run_logger.log_text(f"❌ {message}")
            else:
                self.run_logger.log_text(f"   {message}")
        logger.info(message)
