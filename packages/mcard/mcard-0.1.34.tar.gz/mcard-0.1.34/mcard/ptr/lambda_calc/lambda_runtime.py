"""
Lambda Runtime - PTR interface for Lambda Calculus

Provides a unified runtime interface for Lambda Calculus operations,
integrating the parser and all conversion modules.

This module provides Python parity with mcard-js/src/ptr/lambda/LambdaRuntime.ts
"""

import re
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass

from mcard.model.card_collection import CardCollection
from mcard.ptr.lambda_calc.lambda_term import (
    LambdaTerm, VarTerm, AbsTerm, AppTerm,
    mk_var, mk_abs, mk_app,
    store_term, load_term, pretty_print_deep
)
from mcard.ptr.lambda_calc.free_variables import (
    free_variables, bound_variables, is_closed
)
from mcard.ptr.lambda_calc.alpha_conversion import (
    alpha_rename, alpha_equivalent, alpha_normalize
)
from mcard.ptr.lambda_calc.beta_reduction import (
    beta_reduce, normalize, is_normal_form, is_redex,
    NormalizationResult, ReductionStrategy
)
from mcard.ptr.lambda_calc.eta_conversion import (
    eta_reduce, eta_expand, eta_equivalent, beta_eta_normalize
)


# ─────────────────────────────────────────────────────────────────────────────
# Parser
# ─────────────────────────────────────────────────────────────────────────────

class ParseError(Exception):
    """Error during Lambda expression parsing"""
    pass


def parse_lambda_expression(collection: CardCollection, expr: str) -> str:
    """
    Parse a Lambda expression string and store terms in collection.
    
    Syntax:
      <term> ::= <var> | <abs> | <app> | "(" <term> ")"
      <var>  ::= [a-zA-Z][a-zA-Z0-9']*
      <abs>  ::= ("λ" | "\\") <var> "." <term>
      <app>  ::= <term> <term>
    
    Returns the hash of the parsed term.
    """
    parser = LambdaParser(collection, expr)
    return parser.parse()


class LambdaParser:
    """Recursive descent parser for Lambda expressions"""
    
    def __init__(self, collection: CardCollection, input_str: str):
        self.collection = collection
        self.input = input_str.strip()
        self.pos = 0
    
    def parse(self) -> str:
        """Parse the entire input and return term hash"""
        result = self._parse_term()
        self._skip_whitespace()
        if self.pos < len(self.input):
            raise ParseError(f"Unexpected character at position {self.pos}: '{self.input[self.pos]}'")
        return result
    
    def _skip_whitespace(self):
        """Skip whitespace characters"""
        while self.pos < len(self.input) and self.input[self.pos] in ' \t\n\r':
            self.pos += 1
    
    def _peek(self) -> Optional[str]:
        """Look at current character without consuming"""
        self._skip_whitespace()
        if self.pos >= len(self.input):
            return None
        return self.input[self.pos]
    
    def _consume(self, char: str):
        """Consume expected character"""
        self._skip_whitespace()
        if self.pos >= len(self.input):
            raise ParseError(f"Expected '{char}' but reached end of input")
        if self.input[self.pos] != char:
            raise ParseError(f"Expected '{char}' but found '{self.input[self.pos]}' at position {self.pos}")
        self.pos += 1
    
    def _parse_term(self) -> str:
        """Parse a Lambda term (handles application as left-associative)"""
        atoms = []
        
        while True:
            atom = self._parse_atom()
            if atom is None:
                break
            atoms.append(atom)
        
        if not atoms:
            raise ParseError(f"Expected term at position {self.pos}")
        
        # Build left-associative application
        result = atoms[0]
        for i in range(1, len(atoms)):
            result = store_term(self.collection, mk_app(result, atoms[i]))
        
        return result
    
    def _parse_atom(self) -> Optional[str]:
        """Parse an atomic term (variable, abstraction, or parenthesized)"""
        self._skip_whitespace()
        
        if self.pos >= len(self.input):
            return None
        
        c = self.input[self.pos]
        
        # Lambda/backslash - abstraction
        if c == 'λ' or c == '\\':
            return self._parse_abstraction()
        
        # Open paren - grouped term
        if c == '(':
            return self._parse_grouped()
        
        # Variable
        if c.isalpha():
            return self._parse_variable()
        
        return None
    
    def _parse_variable(self) -> str:
        """Parse a variable name"""
        self._skip_whitespace()
        start = self.pos
        
        # First character must be letter
        if self.pos >= len(self.input) or not self.input[self.pos].isalpha():
            raise ParseError(f"Expected variable at position {self.pos}")
        
        # Read variable name
        while (self.pos < len(self.input) and 
               (self.input[self.pos].isalnum() or self.input[self.pos] == "'")):
            self.pos += 1
        
        name = self.input[start:self.pos]
        return store_term(self.collection, mk_var(name))
    
    def _parse_abstraction(self) -> str:
        """Parse an abstraction: λx.M or \\x.M"""
        self._skip_whitespace()
        
        # Consume lambda symbol
        if self.input[self.pos] == 'λ':
            self.pos += 1
        elif self.input[self.pos] == '\\':
            self.pos += 1
        else:
            raise ParseError(f"Expected λ or \\ at position {self.pos}")
        
        self._skip_whitespace()
        
        # Parse parameter
        start = self.pos
        while (self.pos < len(self.input) and 
               (self.input[self.pos].isalnum() or self.input[self.pos] == "'")):
            self.pos += 1
        
        if self.pos == start:
            raise ParseError(f"Expected parameter name at position {self.pos}")
        
        param = self.input[start:self.pos]
        
        # Consume dot
        self._skip_whitespace()
        self._consume('.')
        
        # Parse body
        body = self._parse_term()
        
        return store_term(self.collection, mk_abs(param, body))
    
    def _parse_grouped(self) -> str:
        """Parse a parenthesized term: (M)"""
        self._consume('(')
        term = self._parse_term()
        self._consume(')')
        return term


# ─────────────────────────────────────────────────────────────────────────────
# Lambda Runtime
# ─────────────────────────────────────────────────────────────────────────────

LambdaOperation = Literal[
    'parse',
    'normalize',
    'normalize-applicative',
    'normalize-lazy',
    'beta-reduce',
    'alpha-equiv',
    'alpha-normalize',
    'eta-reduce',
    'eta-expand',
    'free-vars',
    'is-closed',
    'pretty-print'
]


@dataclass
class LambdaConfig:
    """Configuration for Lambda runtime operations"""
    operation: LambdaOperation = 'normalize'
    strategy: ReductionStrategy = 'normal'
    max_steps: int = 100


@dataclass
class LambdaRuntimeResult:
    """Result from Lambda runtime execution"""
    success: bool
    term_hash: Optional[str] = None
    pretty_print: Optional[str] = None
    free_variables: Optional[List[str]] = None
    is_closed: Optional[bool] = None
    steps: Optional[int] = None
    alpha_equivalent: Optional[bool] = None
    eta_equivalent: Optional[bool] = None
    error: Optional[str] = None


class LambdaRuntime:
    """
    Lambda Calculus runtime for PTR.
    
    Provides α-β-η conversions on MCard-stored Lambda terms.
    """
    
    def __init__(self, collection: CardCollection):
        self.collection = collection
    
    def execute(
        self,
        code_or_hash: str,
        context: Dict[str, Any],
        config: Dict[str, Any],
        chapter_dir: str = ''
    ) -> LambdaRuntimeResult:
        """
        Execute a Lambda operation.
        
        Args:
            code_or_hash: Either a Lambda expression string or a term hash
            context: Additional context (may contain 'expression', 'other_hash')
            config: Operation configuration
            chapter_dir: Working directory (unused)
        
        Returns:
            LambdaRuntimeResult with operation output
        """
        try:
            operation = config.get('operation', 'normalize')
            strategy = config.get('strategy', 'normal')
            max_steps = config.get('max_steps', config.get('maxSteps', 100))
            
            # Parse expression if provided in context
            if context.get('expression'):
                term_hash = parse_lambda_expression(self.collection, context['expression'])
            elif code_or_hash and len(code_or_hash) == 64:
                # Looks like a hash
                term_hash = code_or_hash
            elif code_or_hash and code_or_hash.strip():
                # Parse as expression
                term_hash = parse_lambda_expression(self.collection, code_or_hash)
            else:
                return LambdaRuntimeResult(success=False, error="No expression or hash provided")
            
            # Execute operation
            if operation == 'parse':
                return self._parse(context)
            
            elif operation == 'normalize':
                return self._normalize(term_hash, strategy, max_steps)
            
            elif operation == 'normalize-applicative':
                return self._normalize(term_hash, 'applicative', max_steps)
            
            elif operation == 'normalize-lazy':
                return self._normalize(term_hash, 'lazy', max_steps)
            
            elif operation == 'beta-reduce':
                return self._beta_reduce(term_hash)
            
            elif operation == 'alpha-equiv':
                other_hash = context.get('other_hash')
                if not other_hash:
                    return LambdaRuntimeResult(success=False, error="alpha-equiv requires 'other_hash' in context")
                return self._alpha_equiv(term_hash, other_hash)
            
            elif operation == 'alpha-normalize':
                return self._alpha_normalize(term_hash)
            
            elif operation == 'eta-reduce':
                return self._eta_reduce(term_hash)
            
            elif operation == 'eta-expand':
                return self._eta_expand(term_hash)
            
            elif operation == 'free-vars':
                return self._free_vars(term_hash)
            
            elif operation == 'is-closed':
                return self._is_closed(term_hash)
            
            elif operation == 'pretty-print':
                return self._pretty_print(term_hash)
            
            else:
                return LambdaRuntimeResult(success=False, error=f"Unknown operation: {operation}")
        
        except ParseError as e:
            return LambdaRuntimeResult(success=False, error=f"Parse error: {str(e)}")
        except Exception as e:
            return LambdaRuntimeResult(success=False, error=str(e))
    
    def _parse(self, context: Dict[str, Any]) -> LambdaRuntimeResult:
        """Parse a Lambda expression"""
        expr = context.get('expression', '')
        if not expr:
            return LambdaRuntimeResult(success=False, error="No expression to parse")
        
        term_hash = parse_lambda_expression(self.collection, expr)
        pretty = pretty_print_deep(self.collection, term_hash)
        
        return LambdaRuntimeResult(
            success=True,
            term_hash=term_hash,
            pretty_print=pretty
        )
    
    def _normalize(self, term_hash: str, strategy: str, max_steps: int) -> LambdaRuntimeResult:
        """Normalize a term"""
        result = normalize(self.collection, term_hash, strategy, max_steps)
        
        if result is None:
            return LambdaRuntimeResult(success=False, error="Normalization failed or diverged")
        
        pretty = pretty_print_deep(self.collection, result.normal_form)
        
        return LambdaRuntimeResult(
            success=True,
            term_hash=result.normal_form,
            pretty_print=pretty,
            steps=result.steps
        )
    
    def _beta_reduce(self, term_hash: str) -> LambdaRuntimeResult:
        """Single beta reduction step"""
        result = beta_reduce(self.collection, term_hash)
        
        if result is None:
            return LambdaRuntimeResult(success=False, error="Not a redex")
        
        pretty = pretty_print_deep(self.collection, result)
        
        return LambdaRuntimeResult(
            success=True,
            term_hash=result,
            pretty_print=pretty
        )
    
    def _alpha_equiv(self, hash1: str, hash2: str) -> LambdaRuntimeResult:
        """Check alpha equivalence"""
        equiv = alpha_equivalent(self.collection, hash1, hash2)
        
        if equiv is None:
            return LambdaRuntimeResult(success=False, error="Terms not found")
        
        return LambdaRuntimeResult(
            success=True,
            alpha_equivalent=equiv
        )
    
    def _alpha_normalize(self, term_hash: str) -> LambdaRuntimeResult:
        """Normalize bound variable names"""
        result = alpha_normalize(self.collection, term_hash)
        
        if result is None:
            return LambdaRuntimeResult(success=False, error="Alpha normalization failed")
        
        pretty = pretty_print_deep(self.collection, result)
        
        return LambdaRuntimeResult(
            success=True,
            term_hash=result,
            pretty_print=pretty
        )
    
    def _eta_reduce(self, term_hash: str) -> LambdaRuntimeResult:
        """Eta reduce a term"""
        result = eta_reduce(self.collection, term_hash)
        
        if result is None:
            return LambdaRuntimeResult(success=False, error="Eta reduction failed")
        
        pretty = pretty_print_deep(self.collection, result)
        
        return LambdaRuntimeResult(
            success=True,
            term_hash=result,
            pretty_print=pretty
        )
    
    def _eta_expand(self, term_hash: str) -> LambdaRuntimeResult:
        """Eta expand a term"""
        result = eta_expand(self.collection, term_hash)
        
        if result is None:
            return LambdaRuntimeResult(success=False, error="Eta expansion failed")
        
        pretty = pretty_print_deep(self.collection, result)
        
        return LambdaRuntimeResult(
            success=True,
            term_hash=result,
            pretty_print=pretty
        )
    
    def _free_vars(self, term_hash: str) -> LambdaRuntimeResult:
        """Get free variables"""
        fv = free_variables(self.collection, term_hash)
        
        if fv is None:
            return LambdaRuntimeResult(success=False, error="Term not found")
        
        return LambdaRuntimeResult(
            success=True,
            term_hash=term_hash,
            free_variables=sorted(list(fv))
        )
    
    def _is_closed(self, term_hash: str) -> LambdaRuntimeResult:
        """Check if term is closed"""
        closed = is_closed(self.collection, term_hash)
        
        if closed is None:
            return LambdaRuntimeResult(success=False, error="Term not found")
        
        pretty = pretty_print_deep(self.collection, term_hash)
        
        return LambdaRuntimeResult(
            success=True,
            term_hash=term_hash,
            pretty_print=pretty,
            is_closed=closed
        )
    
    def _pretty_print(self, term_hash: str) -> LambdaRuntimeResult:
        """Pretty print a term"""
        pretty = pretty_print_deep(self.collection, term_hash)
        
        return LambdaRuntimeResult(
            success=True,
            term_hash=term_hash,
            pretty_print=pretty
        )
