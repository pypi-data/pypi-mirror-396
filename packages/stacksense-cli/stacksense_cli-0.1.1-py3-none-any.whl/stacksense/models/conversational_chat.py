"""
Conversational Chat Model with intelligent context usage
"""
import time
import asyncio
from typing import Dict, Any, Optional
from .base import BaseChatModel, StreamingChatModel
import json


class ConversationalChatModel(StreamingChatModel):
    """Chat model for Ollama (local AI)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider = 'ollama'  # Only Ollama now
        self.model_name = config.get('model') or config.get('model_name', 'phi3:mini')
        self.is_conversational = True
        self.debug = config.get('debug', False)  # Debug flag
        
        # Keep-alive tracking
        self.last_heartbeat = None
        self.heartbeat_interval = 45  # seconds
        self.model_warmed = False
        
        # API endpoint
        self.ollama_url = "http://localhost:11434/api/chat"
        
        # Message history
        self.messages = []
        
        # ==== CITATION SYSTEM (100% accuracy!) ====
        self.use_enhanced_citations = config.get('enhanced_citations', True)  # Default: ON
        
        if self.use_enhanced_citations:
            try:
                from ..two_phase_citation import TwoPhaseCitationSystem
                from ..citation_fixer import CitationAutoFixer
                
                self.citation_system = TwoPhaseCitationSystem(
                    model_name=self.model_name,
                    debug=self.debug
                )
                self.citation_fixer = CitationAutoFixer(debug=self.debug)
                
                if self.debug:
                    print(f"[Citations] Enhanced system enabled for {self.model_name}")
            except ImportError as e:
                if self.debug:
                    print(f"[Citations] Failed to load citation system: {e}")
                self.use_enhanced_citations = False
                self.citation_system = None
                self.citation_fixer = None
        else:
            self.citation_system = None
            self.citation_fixer = None
    
    def get_model_config(self) -> Dict[str, Any]:
        """
        Get optimized configuration based on model size.
        Dynamically determines settings from model name patterns.
        
        Returns model-specific settings for token limits, temperature, etc.
        """
        model_lower = self.model_name.lower()
        
        # Size-based heuristics (prod-ready for unknown models)
        if any(x in model_lower for x in ['70b', '72b', '65b']):
            # Huge models (70B+) - aggressive limits
            config = {
                'max_tokens': 200,
                'temperature': 0.5,
                'context_max_files': 1,
                'description': 'Huge model (70B+) - very slow but highest quality'
            }
        
        elif any(x in model_lower for x in ['13b', '14b', '20b', '30b', '34b']):
            # Large models (13B-34B) - moderate limits
            config = {
                'max_tokens': 300,
                'temperature': 0.6,
                'context_max_files': 2,
                'description': 'Large model - slow but high quality'
            }
        
        elif any(x in model_lower for x in ['7b', '8b', '9b']):
            # Medium models (7B-9B) - balanced
            config = {
                'max_tokens': 400,
                'temperature': 0.6,
                'context_max_files': 3,
                'description': 'Medium model - balanced speed/quality'
            }
        
        elif any(x in model_lower for x in ['3b', '4b']):
            # Small models (3B-4B) - generous limits
            config = {
                'max_tokens': 600,
                'temperature': 0.7,
                'context_max_files': 4,
                'description': 'Small model - fast'
            }
        
        else:
            # Tiny models (2B or unknown) - maximum context
            config = {
                'max_tokens': 1000,
                'temperature': 0.7,
                'context_max_files': 5,
                'description': 'Tiny/unknown model - fastest'
            }
        
        if self.debug:
            print(f"[Model Config] {self.model_name}: max_tokens={config['max_tokens']}, "
                  f"compression={config['context_max_files']} files/module")
        
        return config
    
    def get_system_prompt(self) -> str:
        """System prompt with few-shot examples for accuracy"""
        return """You are an expert coding assistant analyzing a codebase.

## PRIMARY DIRECTIVE: USE EXTRACTED CODE FACTS

When codebase context is provided:
1. **CITE SPECIFIC DETAILS** from the extracted code
2. **USE EXACT VALUES** (e.g., ROLE_CHOICES, field names) 
3. **NEVER GUESS** - if details aren't in context, say so
4. **REFERENCE FILES** when mentioning code

## FEW-SHOT EXAMPLES

### Example 1: Good Answer (Uses Extracted Details)
Query: "What user roles exist in the system?"
Context:
```
## EXTRACTED CODE DETAILS
### User (class)
Source: `core/models/user.py`

CHOICES (Exact Values):
`ROLE_CHOICES`:
  - `SAINT`: Saint
  - `GGF`: Growth Group Facilitator
  - `PGC`: People Group Coordinator
```

✅ GOOD Answer:
"Based on `core/models/user.py`, the system defines 3 user roles in `ROLE_CHOICES`:
1. **SAINT**: Saint (regular members)
2. **GGF**: Growth Group Facilitator  
3. **PGC**: People Group Coordinator

These are the exact roles defined in the codebase."

❌ BAD Answer:
"The system likely has roles like admin, moderator, and regular users."

### Example 2: Good Answer (Architecture Question)
Query: "How does authentication work?"
Context:
```
## MODULES
**Authentication Module**
  Handles JWT token generation and validation
  Key features: login, logout, token refresh
```

✅ GOOD Answer:
"Based on the Authentication Module, the system handles:
- JWT token generation
- Token validation
- Login/logout flows
- Token refresh

The module appears JWT-based for stateless authentication."

❌ BAD Answer:
"It probably uses sessions or OAuth2."

### Example 3: When Details Are Missing
Query: "What payment providers are integrated?"
Context:
```
## MODULES
**Payment Module**
  Handles payment processing
```

✅ GOOD Answer:
"The codebase has a Payment Module that handles payment processing. However, the specific payment providers (e.g., Stripe, PayPal) aren't visible in the current extracted context. You may need to check the module's implementation files for provider details."

❌ BAD Answer:
"It probably uses Stripe or PayPal."

## RESPONSE FORMAT

Always structure answers as:

**Source:** [file/module name]

**Key Details:**
- [Fact 1 from code]
- [Fact 2 from code]

**Explanation:**
[Your analysis using those facts]

Remember: Accuracy > Completeness. Say "not visible in context" rather than guess!
"""
    
    async def generate_response(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate conversational response with intelligent web search"""
        
        if context is None:
            context = {}
        
        # ==== INTELLIGENT CONTEXT BUILDING (Phase 3!) ====
        if context:
            try:
                from ..context_builder import build_context
                
                # Build optimized context based on query
                optimized_context = build_context(
                    scan_context=context,
                    query=user_message,
                    depth="auto",  # Auto-detect depth
                    debug=self.debug
                )
                
                if self.debug:
                    depth = optimized_context.get('context_depth', 'unknown')
                    print(f"[Context] Using {depth} context for query")
                    
                    # Show what code details are included
                    if 'code_details' in optimized_context:
                        details_count = len(optimized_context['code_details'])
                        print(f"[Context] Included {details_count} code details with CHOICES/fields")
                
                # Replace with optimized context
                context = optimized_context
            
            except Exception as e:
                if self.debug:
                    print(f"[Context] Builder failed, using original context: {e}")
        
        # ==== FORMAT CONTEXT AS MARKDOWN (CRITICAL FOR ACCURACY!) ====
        context_msg = ""
        if context:
            try:
                from ..context_formatter import format_context
                
                # Convert JSON to human-readable markdown
                context_msg = format_context(context, user_message, debug=self.debug)
                
                if self.debug:
                    print(f"[Formatter] Context: {len(context_msg)} chars")
                    
                    # 🔍 DIAGNOSTIC: Show what AI actually sees
                    print("\n" + "="*80)
                    print("🔍 CONTEXT BEING SENT TO AI:")
                    print("="*80)
                    
                    # Show first 1500 chars
                    preview = context_msg[:1500]
                    print(preview)
                    
                    # Check for specific patterns
                    if 'ROLE_CHOICES' in context_msg:
                        print("\n✅ ROLE_CHOICES detected in context!")
                    else:
                        print("\n⚠️  ROLE_CHOICES NOT in context")
                    
                    if 'User (class)' in context_msg or 'User model' in context_msg:
                        print("✅ User model detected in context!")
                    else:
                        print("⚠️  User model NOT in context")
                    
                    print("="*80 + "\n")
            
            except Exception as e:
                if self.debug:
                    print(f"[Formatter] Failed, using original: {e}")
                # Fallback to JSON
                context_msg = json.dumps(context, indent=2, default=str)
        
        # ==== PRE-WARM MODEL (first time only) ====
        if not self.model_warmed:
            await self.warm_up_model()
    
    def should_search_web(self, query: str, context: dict) -> bool:
        """
        INTELLIGENT web search decision using context sufficiency check.
        
        Tiered Logic:
        1. Explicit external knowledge request → SEARCH
        2. Repo-specific question → NO SEARCH
        3. Architecture/structure question → NO SEARCH (hard rule)
        4. Ambiguous → Calculate context relevance score
        
        This makes StackSense feel intelligent, not reactive.
        """
        query_lower = query.lower()
        
        # ==== TIER 1: EXPLICIT EXTERNAL TRIGGERS ====
        # User explicitly wants external/latest info
        explicit_external = [
            'latest', 'newest', 'recent', 'current version',
            'official documentation', 'api reference',
            'search web', 'look up online', 'google',
            'stackoverflow', 'github issue'
        ]
        if any(trigger in query_lower for trigger in explicit_external):
            if self.debug:
                print(f"[Search] EXPLICIT external trigger detected")
            return True
        
        # ==== TIER 2: REPO-SPECIFIC BLOCKERS ====
        # Question explicitly about scanned code
        repo_specific = [
            'my code', 'my project', 'this file', 'this function',
            'this repo', 'this project', 'our codebase',
            'in my', 'from the scan', 'from context'
        ]
        if any(blocker in query_lower for blocker in repo_specific):
            if self.debug:
                print(f"[Search] BLOCKED - Repo-specific question")
            return False
        
        # ==== TIER 3: ARCHITECTURE QUESTION HARD RULE ====
        # These NEVER search - always answerable from context
        architecture_keywords = [
            'how does', 'how do', 'flow between', 'interaction',
            'architecture', 'structure of', 'design of',
            'module relationship', 'how modules', 'overall structure',
            'how components', 'system design'
        ]
        if any(arch in query_lower for arch in architecture_keywords):
            if self.debug:
                print(f"[Search] BLOCKED - Architecture question (context-only)")
            return False
        
        # ==== TIER 4: CONTEXT SUFFICIENCY CHECK ====
        # Calculate relevance score: Can context answer this?
        
        has_context = bool(context and (context.get('modules') or context.get('frameworks')))
        
        if not has_context:
            # No context at all → search allowed for general knowledge
            if self.debug:
                print(f"[Search] ALLOWED - No repo context available")
            return True
        
        # Calculate context relevance score (0.0 - 1.0)
        context_score = self._calculate_context_relevance(query, context)
        
        if self.debug:
            print(f"[Search] Context relevance score: {context_score:.2f}")
        
        # Threshold: 0.75 = high confidence context has the answer
        if context_score > 0.75:
            if self.debug:
                print(f"[Search] BLOCKED - Context sufficient (score > 0.75)")
            return False
        
        # ==== TIER 5: DEFAULT FOR AMBIGUOUS CASES ====
        # Low context score + looks like external question
        external_hints = [
            'best practice', 'recommended way', 'standard approach',
            'how to', 'tutorial', 'guide', 'example of'
        ]
        
        # If low context score AND external hint → search
        if any(hint in query_lower for hint in external_hints):
            if self.debug:
                print(f"[Search] ALLOWED - External knowledge hint + low context score")
            return True
        
        # Default: Don't search if we have context
        if self.debug:
            print(f"[Search] BLOCKED - Context available, no explicit triggers")
        return False
    
    def _calculate_context_relevance(self, query: str, context: dict) -> float:
        """
        Calculate how well the context can answer the query (0.0 - 1.0).
        
        Scoring factors:
        - Module name matches
        - File name matches
        - Feature/dependency matches
        - Framework matches
        """
        query_words = set(query.lower().split())
        
        # Extract all context keywords
        context_keywords = set()
        
        # From modules
        if context.get('modules'):
            for module in context['modules']:
                # Handle both dict and non-dict modules
                if not isinstance(module, dict):
                    continue
                
                # Module name
                if module.get('name'):
                    context_keywords.update(module['name'].lower().split())
                
                # Files (just basenames for matching)
                if module.get('files'):
                    for file_path in module['files']:
                        basename = file_path.split('/')[-1].lower()
                        context_keywords.add(basename.replace('.py', '').replace('.js', ''))
                
                # Features
                if module.get('features'):
                    for feature in module['features']:
                        context_keywords.update(feature.lower().split())
                
                # Dependencies
                if module.get('dependencies'):
                    for dep in module['dependencies']:
                        context_keywords.add(dep.lower())
        
        # From frameworks
        if context.get('frameworks'):
            frameworks = context['frameworks']
            if isinstance(frameworks, list):
                for fw in frameworks:
                    context_keywords.update(fw.lower().split())
        
        # From patterns
        if context.get('patterns'):
            for pattern_name in context['patterns'].keys():
                context_keywords.add(pattern_name.lower())
        
        # Calculate overlap
        if not context_keywords or not query_words:
            return 0.0
        
        # Overlap calculation
        matches = query_words.intersection(context_keywords)
        overlap_score = len(matches) / len(query_words)
        
        # Boost if query mentions specific files/modules
        if any(word.endswith('.py') or word.endswith('.js') for word in query_words):
            overlap_score += 0.2
        
        # Check overlap with modules
        overlap_count = 0
        total_modules = 0
        
        if context and context.get('modules'):
            for module in context['modules']:
                # Handle both dict and non-dict modules
                if not isinstance(module, dict):
                    continue
                
                total_modules += 1
                if module.get('name') and module['name'].lower() in query.lower():
                    overlap_count += 1
                
                if module.get('description') and any(word in module['description'].lower() for word in query_words):
                    overlap_count += 0.5
        
        return min(overlap_score, 1.0)  # Cap at 1.0
    
    def should_scan_repo(self, user_message: str) -> bool:
        """
        Determine if repo scan is needed.
        Scan only when:
        1. Asking about workspace/repo/codebase
        2. Asking to review/check/analyze code
        """
        message_lower = user_message.lower()
        
        repo_keywords = [
            'repo', 'repository', 'codebase', 'workspace', 'project',
            'code', 'file', 'files',
            'check', 'review', 'analyze', 'scan', 'look at',
            'security', 'performance', 'design', 'structure'
        ]
        
        return any(keyword in message_lower for keyword in repo_keywords)
    
    def get_scan_model(self) -> str:
        """
        Get the optimal model for repo scanning and web searching.
        
        Strategy:
        - Use lightest Ollama model for fast scanning
        - User's chosen model (self.model_name) for interactive chat
        
        Returns:
            Model name for scanning operations
        """
        # For scanning, always use lightest Ollama model if available
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    # Find lightest model
                    model_sizes = []
                    for model in models:
                        name = model.get('name', '')
                        size = model.get('size', 0)
                        size_gb = size / (1024**3) if size else 999
                        model_sizes.append((name, size_gb))
                    
                    model_sizes.sort(key=lambda x: x[1])
                    return model_sizes[0][0]  # Return lightest
        except Exception:
            pass
        
        # Fallback to user's chosen model
        return self.model_name
    
    def _compress_context(self, context: Dict[str, Any], max_files: int = 5) -> Dict[str, Any]:
        """
        Compress context to prevent memory issues and speed up processing.
        
        Limits files per module to top N most important files.
        
        Args:
            context: Full context dict
            max_files: Max files per module (default: 5)
            
        Returns:
            Compressed context dict
        """
        if not context or not context.get('modules'):
            return context
        
        compressed = context.copy()
        compressed['modules'] = []
        
        for module in context['modules']:
            # Handle both dict and string module formats
            if not isinstance(module, dict):
                # Skip non-dict modules
                continue
            
            compressed_module = module.copy()
            
            files = module.get('files', [])
            if len(files) <= max_files:
                compressed['modules'].append(compressed_module)
                continue
            
            # Prioritize important files
            priority_keywords = ['model', 'view', 'handler', 'controller', 'main', 'app', 'api', 'service']
            
            priority_files = []
            other_files = []
            
            for file_path in files:
                basename = file_path.split('/')[-1].lower()
                if any(keyword in basename for keyword in priority_keywords):
                    priority_files.append(file_path)
                else:
                    other_files.append(file_path)
            
            # Take top priority files + fill remaining slots
            selected_files = priority_files[:max_files]
            remaining_slots = max_files - len(selected_files)
            if remaining_slots > 0:
                selected_files.extend(other_files[:remaining_slots])
            
            compressed_module['files'] = selected_files
            compressed_module['_total_files'] = len(files)  # Track original count
            compressed['modules'].append(compressed_module)
        
        return compressed
    
    def _build_context_message(self, context: Optional[Dict[str, Any]]) -> str:
        """
        Build a CLEAR, structured context message for the LLM.
        
        Format context so LLM can easily parse and use it.
        """
        if not context:
            return ""
        
        parts = []
        
        # CRITICAL: Make it obvious this is repo context
        parts.append("=" * 80)
        parts.append("REPOSITORY CONTEXT - YOUR PRIMARY INFORMATION SOURCE")
        parts.append("=" * 80)
        parts.append("")
        
        # Modules (most important - specific code structure)
        if context.get('modules'):
            parts.append("## DETECTED MODULES")
            parts.append("")
            for module in context['modules']:
                parts.append(f"### {module.get('name', 'Unknown Module')}")
                
                if module.get('description'):
                    parts.append(f"**Purpose**: {module['description']}")
                
                if module.get('files'):
                    files = module['files']
                    total_files = module.get('_total_files', len(files))
                    
                    if len(files) <= 5:
                        parts.append(f"**Files**: {', '.join(files)}")
                    else:
                        parts.append(f"**Files** (showing {len(files)} of {total_files}): {', '.join(files[:5])}, ...")
                
                if module.get('features'):
                    parts.append(f"**Features**: {', '.join(module['features'])}")
                
                if module.get('dependencies'):
                    parts.append(f"**Dependencies**: {', '.join(module['dependencies'])}")
                
                parts.append("")
        
        # Frameworks (tech stack)
        if context.get('frameworks'):
            frameworks = context['frameworks']
            if isinstance(frameworks, list):
                parts.append(f"## FRAMEWORKS: {', '.join(frameworks)}")
            else:
                parts.append(f"## FRAMEWORKS: {frameworks}")
            parts.append("")
        
        # Languages (for context)
        if context.get('languages'):
            languages = context['languages']
            if isinstance(languages, dict):
                lang_list = [f"{lang} ({count} files)" for lang, count in languages.items()]
                parts.append(f"## LANGUAGES: {', '.join(lang_list)}")
            else:
                parts.append(f"## LANGUAGES: {languages}")
            parts.append("")
        
        # Patterns (code patterns detected)
        if context.get('patterns'):
            patterns = context['patterns']
            if isinstance(patterns, dict):
                pattern_list = [f"{name} ({count}x)" for name, count in patterns.items() if count > 0]
                if pattern_list:
                    parts.append(f"## CODE PATTERNS: {', '.join(pattern_list[:10])}")
                    parts.append("")
        
        parts.append("=" * 80)
        parts.append("USE THIS CONTEXT FIRST - It's your primary information source!")
        parts.append("=" * 80)
        parts.append("")
        
        # ==== WEB SEARCH RESULTS (SUPPLEMENTAL) ====
        if context.get('web') and context['web'].get('results'):
            parts.append("")
            parts.append("=" * 80)
            parts.append("WEB SEARCH RESULTS - SUPPLEMENTAL INFORMATION")
            parts.append("=" * 80)
            parts.append("")
            
            results = context['web']['results']
            for i, result in enumerate(results[:5], 1):  # Top 5 results
                parts.append(f"## Result {i}: [{result.source.upper()}] {result.title}")
                parts.append(f"**URL**: {result.url}")
                parts.append(f"**Snippet**: {result.snippet[:200]}...")
                
                # Add metadata if available
                if result.metadata:
                    meta_items = []
                    if 'score' in result.metadata:
                        meta_items.append(f"Score: {result.metadata['score']}")
                    if 'answers' in result.metadata:
                        meta_items.append(f"Answers: {result.metadata['answers']}")
                    if 'views' in result.metadata:
                        meta_items.append(f"Views: {result.metadata['views']}")
                    if meta_items:
                        parts.append(f"**Info**: {', '.join(meta_items)}")
                
                parts.append("")
            
            parts.append("=" * 80)
            parts.append("")
        
        return "\n".join(parts)
    
    async def generate_response(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate conversational response with intelligent web search"""
        
        if context is None:
            context = {}
        
        # ==== INTELLIGENT CONTEXT BUILDING (Phase 3!) ====
        if context:
            try:
                from ..context_builder import build_context
                
                # Build optimized context based on query
                optimized_context = build_context(
                    scan_context=context,
                    query=user_message,
                    depth="auto",  # Auto-detect depth
                    debug=self.debug
                )
                
                if self.debug:
                    depth = optimized_context.get('context_depth', 'unknown')
                    print(f"[Context] Using {depth} context for query")
                    
                    # Show what code details are included
                    if 'code_details' in optimized_context:
                        details_count = len(optimized_context['code_details'])
                        print(f"[Context] Included {details_count} code details with CHOICES/fields")
                
                # Replace with optimized context
                context = optimized_context
            
            except Exception as e:
                if self.debug:
                    print(f"[Context] Builder failed, using original context: {e}")
        
        # ==== PRE-WARM MODEL (first time only) ====
        if not self.model_warmed:
            await self.warm_up_model()
        
        # ==== KEEP MODEL ALIVE ====
        await self.keep_alive()
        
        # ==== INTELLIGENT WEB SEARCH DECISION ====
        should_search = self.should_search_web(user_message, context)
        
        # ==== PARALLEL WEB SEARCH (non-blocking) ====
        search_task = None
        if should_search:
            if self.debug:
                print(f"🔍 Web search triggered (running in parallel)")
            
            # Start search in background
            async def search_with_timeout():
                try:
                    from ..web_searcher import WebSearcher
                    searcher = WebSearcher(
                        cache_path=None,
                        debug=self.debug,
                        timeout=10.0
                    )
                    return await searcher.search(user_message)
                except Exception as e:
                    if self.debug:
                        print(f"⚠️  Web search failed: {e}")
                    return None
            
            search_task = asyncio.create_task(search_with_timeout())
        
        # ==== COMPRESS CONTEXT (prevent memory issues) ====
        if context:
            # Use model-specific compression
            model_config = self.get_model_config()
            max_files = model_config['context_max_files']
            
            context = self._compress_context(context, max_files=max_files)
            if self.debug and context.get('modules'):
                total_files = sum(m.get('_total_files', len(m.get('files', []))) for m in context['modules'])
                shown_files = sum(len(m.get('files', [])) for m in context['modules'])
                if total_files > shown_files:
                    print(f"[Context] Compressed: {total_files} files → {shown_files} files (top priority)")
        
        # Build initial context message
        context_msg = self._build_context_message(context)
        
        # ==== WAIT FOR SEARCH (max 10s) ====
        if search_task:
            try:
                search_results = await asyncio.wait_for(search_task, timeout=10.0)
                if search_results:
                    context['web'] = {
                        'results': search_results,
                        'count': len(search_results)
                    }
                    # Rebuild context with search results
                    context_msg = self._build_context_message(context)
                    if self.debug:
                        sources = ', '.join(sorted(set(r.source for r in search_results)))
                        print(f"✅ Found {len(search_results)} web results from: {sources}")
                else:
                    if self.debug:
                        print(f"⚠️  No web results (continuing with context only)")
            except asyncio.TimeoutError:
                if self.debug:
                    print(f"⚠️  Web search timed out after 10s (continuing without)")
        elif self.debug:
            print(f"📦 Using repo context only (no web search)")

        
        # Build messages list
        if not self.messages:
            # First message - add system prompt
            self.messages.append({
                "role": "system",
                "content": self.get_system_prompt()
            })
        
        # Add context if available
        if context_msg:
            self.messages.append({
                "role": "system",
                "content": f"Context for this query:\n{context_msg}"
            })
        
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Generate response based on provider
        if self.provider == 'ollama':
            # _chat_ollama is an async generator - consume it
            response = ""
            async for chunk in self._chat_ollama(stream=False):
                if isinstance(chunk, dict) and "_final" in chunk:
                    # Streaming mode final response
                    response = chunk["_final"]
                elif isinstance(chunk, str):
                    response = chunk
                    break
        else:
            response = await self._chat_ollama()
        
        # ==== ENHANCE CITATIONS (if enabled) ====
        if self.use_enhanced_citations and self.citation_system and context:
            try:
                # Verify current citation quality
                code_extractions = context.get('code_extractions', {})
                if code_extractions:
                    selected_files = list(code_extractions.keys())[:5]  # Top 5 files
                    
                    # Check citation score
                    verification = self.citation_system.verify_citations_simple(
                        response, selected_files
                    )
                    
                    if self.debug:
                        print(f"[Citations] Initial score: {verification['score']:.0f}%")
                    
                    # Auto-fix if below 95%
                    if verification['score'] < 95 and self.citation_fixer:
                        if self.debug:
                            print(f"[Citations] Auto-fixing...")
                        
                        fixed_response, fix_stats = self.citation_fixer.fix_citations(
                            response, context
                        )
                        
                        # Use fixed version if better
                        if fix_stats['citation_rate'] > verification['score']:
                            response = fixed_response
                            if self.debug:
                                print(f"[Citations] Enhanced: {verification['score']:.0f}% → {fix_stats['citation_rate']:.0f}%")
            
            except Exception as e:
                if self.debug:
                    print(f"[Citations] Enhancement failed (using original): {e}")
        
        # Add assistant response to history
        self.messages.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    async def generate_response_streaming(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        show_progress: bool = True
    ):
        """
        Stream response tokens in real-time (makes 75s feel like 3-5s).
        
        Perfect for large models (13B+) where generation takes 60-120s.
        Shows progress and yields tokens as they generate.
        
        Args:
            user_message: User's query
            context: Repository context
            show_progress: Show progress messages
            
        Yields:
            dict: Progress and tokens
                {"type": "progress", "message": "Analyzing..."}
                {"type": "token", "content": "To"}
                {"type": "complete", "full_response": "..."}
        """
        import time
        
        if context is None:
            context = {}
        
        start_time = time.time()
        
        # Stage 1: Pre-warm
        if not self.model_warmed:
            if show_progress:
                yield {"type": "progress", "message": "🔥 Starting model..."}
            await self.warm_up_model()
        
        # Stage 2: Keep alive
        await self.keep_alive()
        
        # Stage 3: Analyze
        if show_progress:
            yield {"type": "progress", "message": "🔍 Analyzing query..."}
        
        should_search = self.should_search_web(user_message, context)
        
        # Stage 4: Search (parallel)
        search_task = None
        if should_search:
            if show_progress:
                yield {"type": "progress", "message": "🌐 Searching web..."}
            
            async def search_with_timeout():
                try:
                    from ..web_searcher import WebSearcher
                    searcher = WebSearcher(cache_path=None, debug=self.debug, timeout=10.0)
                    return await searcher.search(user_message)
                except Exception as e:
                    if self.debug:
                        print(f"⚠️  Search failed: {e}")
                    return None
            
            search_task = asyncio.create_task(search_with_timeout())
        
        # Stage 5: Compress context
        if show_progress:
            yield {"type": "progress", "message": "📦 Preparing context..."}
        
        if context:
            model_config = self.get_model_config()
            context = self._compress_context(context, max_files=model_config['context_max_files'])
        
        context_msg = self._build_context_message(context)
        
        # Stage 6: Wait for search
        if search_task:
            try:
                search_results = await asyncio.wait_for(search_task, timeout=10.0)
                if search_results:
                    context['web'] = {'results': search_results, 'count': len(search_results)}
                    context_msg = self._build_context_message(context)
            except asyncio.TimeoutError:
                if self.debug:
                    print("⚠️  Search timeout")
        
        # Stage 7: Build messages
        if not self.messages:
            self.messages.append({"role": "system", "content": self.get_system_prompt()})
        
        if context_msg:
            self.messages.append({"role": "system", "content": f"Context:\n{context_msg}"})
        
        self.messages.append({"role": "user", "content": user_message})
        
        # Stage 8: Stream response
        if show_progress:
            yield {"type": "progress", "message": "💭 Generating response..."}
            yield {"type": "stream_start"}
        
        full_response = ""
        first_token_time = None
        
        if self.provider == 'ollama':
            async for token in self._chat_ollama(stream=True):
                # Handle both string tokens and final dict
                if isinstance(token, dict) and "_final" in token:
                    # This is the final full response from generator
                    full_response = token["_final"]
                    break
                elif isinstance(token, str):
                    if not first_token_time:
                        first_token_time = time.time()
                        if self.debug:
                            print(f"\n[Stream] First token: {first_token_time - start_time:.2f}s")
                    
                    full_response += token
                    yield {"type": "token", "content": token}
        else:
            # TogetherAI fallback
            full_response = await self._chat_ollama()
            yield {"type": "token", "content": full_response}
        
        # Add to history
        self.messages.append({"role": "assistant", "content": full_response})
        
        # Stage 9: Complete
        total_time = time.time() - start_time
        
        yield {
            "type": "complete",
            "full_response": full_response,
            "time_total": total_time,
            "time_to_first_token": first_token_time - start_time if first_token_time else None
        }
    
    async def two_phase_response(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        show_progress: bool = True
    ):
        """
        Two-phase response for large models (13B+).
        
        Phase 1: Instant acknowledgment (<3s)
        Phase 2: Quality streaming response
        
        This makes large models feel instant while delivering quality.
        
        Yields:
            dict: Quick ack + streaming tokens
                {"type": "quick_ack", "message": "Got it..."}
                {"type": "token", "content": "To"}
        """
        import time
        
        # Phase 1: Instant acknowledgment
        if show_progress:
            yield {
                "type": "quick_ack",
                "message": "Got it — analyzing your codebase and preparing a detailed response..."
            }
        
        # Phase 2: Full streaming response
        async for event in self.generate_response_streaming(user_message, context, show_progress=show_progress):
            yield event
    
    async def _chat_ollama(self, stream: bool = False):
        """
        Chat with Ollama with optional streaming.
        
        Args:
            stream: If True, yields tokens as they generate (async generator)
                   If False, returns complete response (string)
        """
        try:
            import aiohttp
            
            # Get model-specific config
            model_config = self.get_model_config()
            
            payload = {
                "model": self.model_name,
                "messages": self.messages,
                "stream": stream,
                "options": {
                    "num_predict": model_config['max_tokens'],
                    "temperature": model_config['temperature']
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.ollama_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        if stream:
                            # Streaming mode - yield tokens as they come
                            full_response = ""
                            async for line in response.content:
                                if line:
                                    try:
                                        data = json.loads(line)
                                        token = data.get('message', {}).get('content', '')
                                        if token:
                                            full_response += token
                                            yield token
                                        
                                        if data.get('done', False):
                                            # Can't return value in generator - just break
                                            break
                                    except json.JSONDecodeError:
                                        continue
                            
                            # Yield final response instead of returning
                            yield {"_final": full_response}
                        else:
                            # Non-streaming mode (not a generator path)
                            data = await response.json()
                            yield data.get('message', {}).get('content', 'No response')
                            return
                    else:
                        error_msg = f"Ollama error: {response.status}"
                        yield error_msg
                        return
        
        except ImportError:
            # Fallback to requests (no streaming support)
            import requests
            model_config = self.get_model_config()
            payload = {
                "model": self.model_name,
                "messages": self.messages,
                "stream": False,
                "options": {
                    "num_predict": model_config['max_tokens'],
                    "temperature": model_config['temperature']
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            if response.status_code == 200:
                data = response.json()
                yield data.get('message', {}).get('content', 'No response')
            else:
                yield f"Ollama error: {response.status_code}"
            return
        
        except Exception as e:
            error_msg = f"Error connecting to Ollama: {e}\n\nMake sure Ollama is running: `ollama serve`"
            yield error_msg
            return
    
    async def warm_up_model(self):
        """Pre-load model into memory to prevent crashes"""
        if self.model_warmed or self.provider != 'ollama':
            return
        
        try:
            if self.debug:
                print(f"[Model] Pre-warming {self.model_name}...")
            
            # Send tiny request to load model
            import aiohttp
            import asyncio
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.ollama_url,
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": "ping"}],
                        "stream": False
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        self.model_warmed = True
                        self.last_heartbeat = asyncio.get_event_loop().time()
                        if self.debug:
                            print(f"[Model] ✅ {self.model_name} pre-warmed and ready")
        except Exception as e:
            if self.debug:
                print(f"[Model] ⚠️  Warm-up failed: {e}")
    
    async def keep_alive(self):
        """Send heartbeat to keep model loaded in memory"""
        if self.provider != 'ollama':
            return
        
        # Check if heartbeat needed
        if self.last_heartbeat:
            import asyncio
            elapsed = asyncio.get_event_loop().time() - self.last_heartbeat
            if elapsed < self.heartbeat_interval:
                return  # Still fresh
        
        try:
            # Quick ping
            import aiohttp
            import asyncio
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.ollama_url,
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": "ping"}],
                        "stream": False
                    },
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        self.last_heartbeat = asyncio.get_event_loop().time()
        except:
            pass  # Silent fail for heartbeat
    
    async def generate_response_stream(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Stream response (for future use)"""
        # For now, just yield the full response
        response = await self.generate_response(user_message, context)
        yield response
