"""
LLM Prompter

This module handles prompting LLMs with processed schema data.
"""

import time
from typing import Dict, Any, Optional, List

from ..analytics import MetricsCollector


class LLMPrompter:
    """Handles LLM prompting with processed schema information."""
    
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, analytics_dir: Optional[str] = None):
        """
        Initialize the LLM Prompter.
        
        Args:
            model: LLM model to use (e.g., 'gpt-4', 'claude-3', etc.)
            api_key: API key for the LLM service (if required)
            analytics_dir: Optional directory for analytics output (uses default if None)
                          Typically should be: <run_output_dir>/analytics/
        """
        self.model = model
        self.api_key = api_key
        analytics_path = analytics_dir or "output/analytics"
        self.metrics_collector = MetricsCollector(analytics_dir=analytics_path)
        # Store context for metrics collection
        self._current_processed_data = None
        self._current_analysis_data = None
        self._current_task = None
    
    def create_prompt(self, processed_data: Dict[str, Any], task: str = "analyze", analysis_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a prompt from processed schema data.
        
        Args:
            processed_data: Processed schema information from SchemaProcessor
            task: The task to perform (e.g., 'analyze', 'document', 'validate', 'gherkin')
            analysis_data: Schema analysis data from SchemaAnalyzer (for Gherkin generation)
            
        Returns:
            Formatted prompt string
            
        Raises:
            ValueError: If required input data is empty or invalid
        """
        # Validate processed_data
        if not processed_data:
            raise ValueError("processed_data cannot be empty or None")
        
        if not isinstance(processed_data, dict):
            raise ValueError(f"processed_data must be a dictionary, got {type(processed_data)}")
        
        # Validate task-specific requirements
        if task == 'gherkin':
            if not analysis_data:
                raise ValueError("analysis_data is required for 'gherkin' task but was None or empty")
            
            if not isinstance(analysis_data, dict):
                raise ValueError(f"analysis_data must be a dictionary, got {type(analysis_data)}")
            
            # Check if analysis_data has endpoints
            endpoints = analysis_data.get('endpoints', [])
            if not endpoints or len(endpoints) == 0:
                raise ValueError("analysis_data contains no endpoints. Cannot generate Gherkin scenarios without endpoints.")
            
            # Check if endpoints list is actually populated
            if not isinstance(endpoints, list):
                raise ValueError(f"analysis_data.endpoints must be a list, got {type(endpoints)}")
        
        prompt_template = self._get_prompt_template(task)
        
        if task == 'gherkin' and analysis_data:
            # Format analysis data as JSON string for the prompt
            import json
            
            # Aggressively optimize and reduce analysis data size
            optimized_analysis = self._aggressively_reduce_analysis_data(analysis_data)
            analysis_json = json.dumps(optimized_analysis, indent=0)  # No indentation to save space
            
            # Estimate tokens (roughly 1 token = 4 characters for English)
            estimated_tokens = len(analysis_json) // 4
            template_tokens = len(prompt_template) // 4
            total_estimated = estimated_tokens + template_tokens
            
            # Target: keep under 5000 tokens to leave room for response (GPT-4 limit is 8192 total)
            # We need: prompt (~2000) + analysis (~3000) + response (3000) = ~8000 total
            max_analysis_tokens = 3000  # Very conservative limit for GPT-4
            
            if estimated_tokens > max_analysis_tokens:
                print(f"⚠ Large schema detected (~{estimated_tokens} tokens). Creating compact summary...")
                # Create a very compact summary
                analysis_json = self._create_compact_summary(analysis_data, max_endpoints=12)
                estimated_tokens = len(analysis_json) // 4
                print(f"   → Reduced to ~{estimated_tokens} tokens")
            
            prompt = prompt_template.format(
                api_name=processed_data.get('info', {}).get('title', 'Unknown API'),
                api_version=processed_data.get('info', {}).get('version', 'Unknown'),
                openapi_version=processed_data.get('version', 'Unknown'),
                analysis_data=analysis_json
            )
            
            # Final token check
            final_tokens = len(prompt) // 4
            if final_tokens > 9000:
                print(f"⚠ Warning: Prompt still large (~{final_tokens} tokens). Consider using chunking.")
        else:
            # Format the prompt with processed data
            prompt = prompt_template.format(
                api_name=processed_data.get('info', {}).get('title', 'Unknown API'),
                api_version=processed_data.get('info', {}).get('version', 'Unknown'),
                openapi_version=processed_data.get('version', 'Unknown'),
                endpoints_count=processed_data.get('paths_count', 0),
                endpoints=self._format_endpoints(processed_data.get('endpoints', [])),
                components=processed_data.get('components', {}),
                tags=processed_data.get('tags', [])
            )
        
        # Validate that prompt is not empty
        if not prompt or not prompt.strip():
            raise ValueError("Generated prompt is empty. Check input data and template.")
        
        # Check minimum prompt length
        if len(prompt.strip()) < 50:
            raise ValueError(f"Generated prompt is too short ({len(prompt.strip())} chars). Minimum 50 characters required.")
        
        return prompt
    
    def _get_prompt_template(self, task: str) -> str:
        """
        Get the prompt template for a specific task.
        
        Args:
            task: The task type
            
        Returns:
            Prompt template string
        """
        templates = {
            'gherkin': """You are an expert in API testing and BDD (Behavior-Driven Development). 

Given the following OpenAPI/Swagger schema analysis, generate comprehensive Gherkin test scenarios.

API Information:
- Name: {api_name}
- Version: {api_version}
- OpenAPI Version: {openapi_version}

Schema Analysis Data:
{analysis_data}

NOTE: In the data above, shortened keys are used to save space:
- 'p' = path
- 'm' = method  
- 'loc' = location (path/query/header/body)
- 'req' = required
- 'params' = parameters

CRITICAL INSTRUCTIONS:
1. Generate Gherkin scenarios (Given-When-Then format) for each endpoint
2. Include positive test cases (happy paths)
3. Include negative test cases (error scenarios, invalid inputs)
4. Include edge cases (boundary values, edge conditions)
5. Include security test cases (authentication, authorization)
6. For each scenario, include:
   - Feature name
   - Scenario name
   - Given/When/Then steps
   - Example data tables where applicable
   - Tags for categorization

OUTPUT FORMAT REQUIREMENTS:
- Use proper Gherkin syntax EXACTLY as shown below
- DO NOT wrap output in markdown code blocks
- DO NOT add any explanatory text before or after the Gherkin
- Start directly with "Feature:" keyword
- Each scenario must start with "Scenario:" keyword
- Steps must start with "Given ", "When ", or "Then " (capitalized, with space)
- Be specific with test data
- Include assertions for expected responses
- Cover all HTTP methods and status codes
- Test all parameter types (path, query, header, body)

EXAMPLE FORMAT:
Feature: API Name Testing

  Scenario: Test endpoint name
    Given I have valid test data
    When I send a GET request to "/endpoint"
    Then I should receive a 200 OK response

  Scenario: Test with invalid data
    Given I have invalid test data
    When I send a POST request to "/endpoint"
    Then I should receive a 400 Bad Request response

Generate comprehensive test scenarios in Gherkin format (start with Feature:):
""",
            'analyze': """Analyze the following OpenAPI/Swagger schema:

API Name: {api_name}
API Version: {api_version}
OpenAPI Version: {openapi_version}

Endpoints: {endpoints_count}
{endpoints}

Components:
- Schemas: {components[schemas_count]}
- Responses: {components[responses_count]}
- Parameters: {components[parameters_count]}
- Security Schemes: {components[security_schemes_count]}

Tags: {tags}

Please provide:
1. A summary of the API's purpose and main functionality
2. Key endpoints and their purposes
3. Any potential issues or improvements
4. Security considerations
""",
            'document': """Generate comprehensive documentation for this API:

API: {api_name} v{api_version}
OpenAPI Version: {openapi_version}

Endpoints ({endpoints_count}):
{endpoints}

Please create:
1. Overview documentation
2. Endpoint documentation
3. Request/response examples
4. Authentication guide
""",
            'validate': """Validate this API schema:

API: {api_name} v{api_version}
OpenAPI Version: {openapi_version}

Endpoints: {endpoints_count}
{endpoints}

Please check for:
1. Missing required fields
2. Inconsistent naming conventions
3. Missing documentation
4. Security best practices
5. RESTful design principles
"""
        }
        
        return templates.get(task, templates['analyze'])
    
    def _format_endpoints(self, endpoints: List[Dict[str, Any]]) -> str:
        """
        Format endpoints list for prompt.
        
        Args:
            endpoints: List of endpoint dictionaries
            
        Returns:
            Formatted string of endpoints
        """
        if not endpoints:
            return "No endpoints found"
        
        formatted = []
        for endpoint in endpoints[:20]:  # Limit to first 20 for prompt size
            formatted.append(
                f"- {endpoint['method']} {endpoint['path']} "
                f"({endpoint.get('summary', 'No summary')})"
            )
        
        if len(endpoints) > 20:
            formatted.append(f"\n... and {len(endpoints) - 20} more endpoints")
        
        return "\n".join(formatted)
    
    def send_prompt(self, prompt: str) -> Optional[str]:
        """
        Send prompt to LLM and get response.
        
        Args:
            prompt: The prompt string to send
            
        Returns:
            LLM response, or None if error
            
        Raises:
            ValueError: If prompt is empty or invalid
        """
        # Validate prompt input
        if not prompt:
            raise ValueError("prompt cannot be empty or None")
        
        if not isinstance(prompt, str):
            raise ValueError(f"prompt must be a string, got {type(prompt)}")
        
        prompt = prompt.strip()
        if not prompt:
            raise ValueError("prompt cannot be empty or whitespace only")
        
        if len(prompt) < 10:
            raise ValueError(f"prompt is too short ({len(prompt)} chars). Minimum 10 characters required.")
        
        if not self.api_key:
            print("⚠ Warning: No API key provided. Using placeholder.")
            print("=" * 60)
            print("LLM Prompt (API key not set)")
            print("=" * 60)
            print(prompt)
            print("=" * 60)
            print("\n[LLM response would appear here after API key is set]")
            return None
        
        # Track execution time
        start_time = time.time()
        api_response = None
        
        try:
            from openai import OpenAI
            
            # Initialize OpenAI client
            client = OpenAI(api_key=self.api_key)
            
            # Use the model if specified, otherwise default to gpt-4
            model = self.model or "gpt-4"
            
            print(f"🤖 Sending prompt to {model}...")
            
            # Check prompt size (OpenAI has limits)
            # More accurate: ~1 token = 4 characters for English text
            prompt_tokens_estimate = len(prompt) // 4
            max_tokens_for_response = 3000  # We set max_tokens=3000
            total_estimated = prompt_tokens_estimate + max_tokens_for_response
            
            if total_estimated > 8000:  # GPT-4 limit is 8192
                print(f"⚠ Warning: Large prompt detected (~{prompt_tokens_estimate} tokens input + {max_tokens_for_response} output = ~{total_estimated} total)")
                print(f"   GPT-4 limit is 8192 tokens. Reducing chunk size or using compact summary...")
                # If we're over limit, we should have chunked or reduced more
                if total_estimated > 8192:
                    raise ValueError(f"Prompt too large ({total_estimated} tokens) for GPT-4 (8192 limit). Use smaller chunks or different model.")
            
            # Make API call with increased max_tokens and retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    api_response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert in API testing and BDD (Behavior-Driven Development). Generate comprehensive Gherkin test scenarios based on OpenAPI/Swagger schema analysis. Always output valid Gherkin syntax starting with 'Feature:' keyword."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=3000  # Reduced to fit within 8192 token limit (GPT-4)
                    )
                    break  # Success, exit retry loop
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"⚠ Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise retry_error
            
            # Extract the response content
            if not api_response.choices or not api_response.choices[0].message.content:
                print("✗ Error: Empty response from LLM")
                return None
            
            gherkin_content = api_response.choices[0].message.content.strip()
            
            # Validate that we got actual Gherkin content
            if not gherkin_content or len(gherkin_content) < 50:
                print(f"⚠ Warning: Very short response ({len(gherkin_content)} chars)")
                print(f"   Response: {gherkin_content[:200]}")
                return None
            
            # Check if it looks like Gherkin
            if not gherkin_content.lower().startswith('feature'):
                print("⚠ Warning: Response doesn't start with 'Feature:' keyword")
                print(f"   First 200 chars: {gherkin_content[:200]}")
                # Try to extract Gherkin if it's wrapped in markdown
                if '```' in gherkin_content:
                    # Extract from code block
                    import re
                    match = re.search(r'```(?:gherkin)?\s*\n(.*?)\n```', gherkin_content, re.DOTALL | re.IGNORECASE)
                    if match:
                        gherkin_content = match.group(1).strip()
                        print("   → Extracted Gherkin from code block")
            
            # Debug: Show first 200 chars of response
            preview = gherkin_content[:200].replace('\n', ' ')
            print(f"✓ Gherkin scenarios generated ({len(gherkin_content)} chars)")
            print(f"   Preview: {preview}...")
            
            return gherkin_content
            
        except ImportError:
            print("⚠ Error: openai package not installed.")
            print("   Run: pip install openai")
            return None
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"✗ Error calling LLM API ({error_type}): {error_msg}")
            
            # Provide more specific error messages
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                print("   → Rate limit exceeded. Please wait and try again.")
            elif "invalid_api_key" in error_msg.lower() or "401" in error_msg:
                print("   → Invalid API key. Please check your OPENAI_API_KEY.")
            elif "insufficient_quota" in error_msg.lower():
                print("   → Insufficient quota. Please check your OpenAI account billing.")
            elif "context_length" in error_msg.lower() or "token" in error_msg.lower():
                print("   → Prompt too long. Try with a smaller schema or increase max_tokens.")
            else:
                print(f"   → Full error: {e}")
            
            return None
        finally:
            # Collect and save metrics after API call (whether successful or not)
            execution_time = time.time() - start_time
            try:
                # Collect general LLM metrics
                metrics = self.metrics_collector.collect_metrics(
                    processed_data=self._current_processed_data,
                    analysis_data=self._current_analysis_data,
                    prompt=prompt,
                    api_response=api_response,
                    execution_time=execution_time,
                    model=self.model or "gpt-4",
                    task=self._current_task
                )
                metrics_file = self.metrics_collector.save_metrics(metrics)
                print(f"📊 Analytics saved: {metrics_file}")
                
                # Collect algorithm-specific metrics for LLM call
                llm_metrics = {
                    'prompt_metrics': metrics.get('prompt_metrics', {}),
                    'api_usage': metrics.get('api_usage', {}),
                    'response_metrics': metrics.get('response_metrics', {})
                }
                
                # Prepare output data
                output_data = {}
                if 'gherkin_content' in locals() and gherkin_content:
                    output_data = {"response_length": len(gherkin_content), "has_response": True}
                else:
                    output_data = {"has_response": False}
                
                algorithm_metrics = self.metrics_collector.collect_algorithm_metrics(
                    algorithm_name="LLMPrompter",
                    algorithm_type="llm_prompter",
                    input_data=self._current_processed_data,
                    output_data=output_data,
                    execution_time=execution_time,
                    complexity_metrics=metrics.get('complexity_analysis', {}),
                    llm_call=True,
                    llm_metrics=llm_metrics
                )
                algorithm_report = self.metrics_collector.save_algorithm_report(algorithm_metrics)
                print(f"📈 Algorithm report saved: {algorithm_report}")
            except Exception as metrics_error:
                print(f"⚠ Warning: Failed to save analytics: {metrics_error}")
    
    def process_and_prompt(self, processed_data: Dict[str, Any], task: str = "analyze", analysis_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create prompt from processed data and send to LLM.
        
        Args:
            processed_data: Processed schema information
            task: The task to perform
            analysis_data: Schema analysis data from SchemaAnalyzer (for Gherkin generation)
            
        Returns:
            LLM response, or None if not implemented
        """
        # Store context for metrics collection
        self._current_processed_data = processed_data
        self._current_analysis_data = analysis_data
        self._current_task = task
        
        prompt = self.create_prompt(processed_data, task, analysis_data)
        return self.send_prompt(prompt)
    
    def _aggressively_reduce_analysis_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggressively reduce analysis data size while keeping essential information.
        
        Args:
            analysis_data: Full analysis data
            
        Returns:
            Heavily optimized analysis data
        """
        if not analysis_data or 'endpoints' not in analysis_data:
            return analysis_data
        
        endpoints = analysis_data.get('endpoints', [])
        total_endpoints = len(endpoints)
        
        # Limit to most important endpoints (prioritize by method diversity)
        max_endpoints = 15  # Further reduced to ensure we stay under token limits
        if total_endpoints > max_endpoints:
            # Prioritize: GET, POST, PUT, DELETE, PATCH in that order
            method_priority = {'GET': 1, 'POST': 2, 'PUT': 3, 'DELETE': 4, 'PATCH': 5}
            endpoints_sorted = sorted(
                endpoints,
                key=lambda e: (method_priority.get(e.get('method', ''), 99), e.get('path', ''))
            )
            endpoints = endpoints_sorted[:max_endpoints]
        
        optimized_endpoints = []
        for endpoint in endpoints:
            # Minimal endpoint data
            opt_endpoint = {
                'p': endpoint.get('path', ''),  # Shortened key
                'm': endpoint.get('method', ''),  # Shortened key
                'params': []  # Shortened key
            }
            
            # Limit parameters per endpoint (max 3 most important to save tokens)
            params = endpoint.get('parameters', [])[:3]
            for param in params:
                # Minimal parameter data
                opt_param = {
                    'loc': param.get('location', ''),  # Shortened
                    'name': param.get('name', ''),
                    'type': param.get('type', ''),
                    'req': param.get('required', False)  # Shortened
                }
                # Only include constraints if they're critical
                constraints = param.get('constraints', {})
                if constraints.get('enum'):
                    opt_param['enum'] = constraints['enum'][:5]  # Limit enum values
                elif constraints.get('pattern'):
                    opt_param['pattern'] = constraints['pattern']
                
                opt_endpoint['params'].append(opt_param)
            
            optimized_endpoints.append(opt_endpoint)
        
        return {
            'endpoints': optimized_endpoints,
            'total': total_endpoints,
            'shown': len(optimized_endpoints)
        }
    
    def _create_compact_summary(self, analysis_data: Dict[str, Any], max_endpoints: int = 12) -> str:
        """
        Create a very compact text summary instead of full JSON.
        
        Args:
            analysis_data: Full analysis data
            max_endpoints: Maximum endpoints to include (default 12 to fit in token limit)
            
        Returns:
            Compact string summary
        """
        endpoints = analysis_data.get('endpoints', [])[:max_endpoints]
        total = len(analysis_data.get('endpoints', []))
        
        # Ultra-compact format: METHOD PATH (param_count)
        summary_lines = [f"Total: {total}, Showing: {len(endpoints)}"]
        
        for endpoint in endpoints:
            path = endpoint.get('path', '')[:50]  # Truncate long paths
            method = endpoint.get('method', '')
            params_count = len(endpoint.get('parameters', []))
            summary_lines.append(f"{method} {path} ({params_count})")
        
        return "\n".join(summary_lines)
    
    def _optimize_analysis_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize analysis data to reduce size while keeping essential information.
        
        Args:
            analysis_data: Full analysis data
            
        Returns:
            Optimized analysis data
            
        Raises:
            ValueError: If analysis_data is empty or invalid
        """
        if not analysis_data:
            raise ValueError("analysis_data cannot be empty or None")
        
        if not isinstance(analysis_data, dict):
            raise ValueError(f"analysis_data must be a dictionary, got {type(analysis_data)}")
        
        optimized = analysis_data.copy()
        
        # Limit detailed parameter information to essential fields
        if 'endpoints' in optimized:
            endpoints = optimized.get('endpoints', [])
            if not endpoints:
                raise ValueError("analysis_data.endpoints is empty. Cannot optimize empty data.")
            
            optimized_endpoints = []
            for endpoint in endpoints:
                if not isinstance(endpoint, dict):
                    continue  # Skip invalid endpoints
                
                optimized_endpoint = {
                    'path': endpoint.get('path', ''),
                    'method': endpoint.get('method', ''),
                    'parameters': []
                }
                
                # Include essential parameter info only
                for param in endpoint.get('parameters', []):
                    if not isinstance(param, dict):
                        continue  # Skip invalid parameters
                    
                    optimized_param = {
                        'location': param.get('location', ''),
                        'name': param.get('name', ''),
                        'type': param.get('type', ''),
                        'required': param.get('required', False),
                        'constraints': param.get('constraints', {}),
                        'iterationCount': param.get('iterationCount')
                    }
                    # Only include notes if they're important
                    if param.get('notes') and len(param.get('notes', '')) < 100:
                        optimized_param['notes'] = param.get('notes')
                    
                    optimized_endpoint['parameters'].append(optimized_param)
                
                optimized_endpoints.append(optimized_endpoint)
            
            if not optimized_endpoints:
                raise ValueError("After optimization, no valid endpoints remain.")
            
            optimized['endpoints'] = optimized_endpoints
        else:
            raise ValueError("analysis_data missing 'endpoints' key")
        
        return optimized
    
    def generate_gherkin_scenarios(self, processed_data: Dict[str, Any], analysis_data: Dict[str, Any], use_chunking: bool = True) -> Optional[str]:
        """
        Generate Gherkin test scenarios from processed and analyzed schema data.
        
        Args:
            processed_data: Processed schema information from SchemaProcessor
            analysis_data: Detailed analysis from SchemaAnalyzer
            use_chunking: If True, split large schemas into chunks
            
        Returns:
            Gherkin scenarios as string, or None if error
            
        Raises:
            ValueError: If input data is empty or invalid
        """
        # Validate inputs before processing
        if not processed_data:
            raise ValueError("processed_data cannot be empty or None for Gherkin generation")
        
        if not analysis_data:
            raise ValueError("analysis_data cannot be empty or None for Gherkin generation")
        
        if not isinstance(processed_data, dict):
            raise ValueError(f"processed_data must be a dictionary, got {type(processed_data)}")
        
        if not isinstance(analysis_data, dict):
            raise ValueError(f"analysis_data must be a dictionary, got {type(analysis_data)}")
        
        # Check if analysis_data has endpoints
        endpoints = analysis_data.get('endpoints', [])
        if not endpoints:
            raise ValueError("analysis_data contains no endpoints. Cannot generate Gherkin scenarios without endpoints.")
        
        if not isinstance(endpoints, list):
            raise ValueError(f"analysis_data.endpoints must be a list, got {type(endpoints)}")
        
        if len(endpoints) == 0:
            raise ValueError("analysis_data.endpoints is an empty list. Cannot generate Gherkin scenarios.")
        
        # Check if we should use chunking for very large schemas
        # Lower threshold to avoid token limit issues (GPT-4 has 8192 token limit)
        if use_chunking and len(endpoints) > 15:
            return self._generate_gherkin_with_chunking(processed_data, analysis_data)
        
        return self.process_and_prompt(processed_data, task="gherkin", analysis_data=analysis_data)
    
    def _generate_gherkin_with_chunking(self, processed_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate Gherkin scenarios by processing endpoints in chunks.
        
        Args:
            processed_data: Processed schema information
            analysis_data: Full analysis data with all endpoints
            
        Returns:
            Combined Gherkin scenarios from all chunks
        """
        endpoints = analysis_data.get('endpoints', [])
        total_endpoints = len(endpoints)
        # Much smaller chunks to ensure we stay under GPT-4's 8192 token limit
        # With aggressive reduction: ~10-15 endpoints per chunk is safe
        chunk_size = 12  # Process 12 endpoints at a time to stay well under limits
        
        print(f"📦 Large schema detected ({total_endpoints} endpoints). Processing in chunks of {chunk_size}...")
        
        all_scenarios = []
        total_chunks = (total_endpoints + chunk_size - 1) // chunk_size
        
        for i in range(0, total_endpoints, chunk_size):
            chunk_endpoints = endpoints[i:i + chunk_size]
            chunk_num = (i // chunk_size) + 1
            
            print(f"   Processing chunk {chunk_num}/{total_chunks} (endpoints {i+1}-{min(i+chunk_size, total_endpoints)})...")
            
            # Create chunked analysis data with aggressive optimization
            chunked_analysis = {
                'endpoints': chunk_endpoints,
                'chunk_info': {
                    'current': chunk_num,
                    'total': total_chunks,
                    'range': f"{i+1}-{min(i+chunk_size, total_endpoints)}"
                }
            }
            
            # Generate scenarios for this chunk
            try:
                chunk_scenarios = self.process_and_prompt(
                    processed_data,
                    task="gherkin",
                    analysis_data=chunked_analysis
                )
                
                if chunk_scenarios:
                    all_scenarios.append(chunk_scenarios)
                    print(f"   ✓ Chunk {chunk_num} completed")
                else:
                    print(f"   ⚠ Chunk {chunk_num} returned empty, skipping...")
            except Exception as e:
                print(f"   ✗ Chunk {chunk_num} failed: {e}")
                # Continue with next chunk
                continue
        
        if not all_scenarios:
            print("✗ All chunks failed to generate scenarios")
            return None
        
        # Combine all scenarios with proper separation
        combined = "\n\n".join(all_scenarios)
        print(f"✓ Generated scenarios from {len(all_scenarios)}/{total_chunks} chunks")
        print(f"   Total scenarios length: {len(combined)} characters")
        
        return combined

