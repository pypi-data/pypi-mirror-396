# DocRAG MCP Tools Comparison

Visual guide to help choose the right tool for your needs.

## Tool Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DocRAG MCP Tools                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ search_docs  │  │answer_question│ │list_indexed_ │    │
│  │              │  │              │  │    docs      │    │
│  │   Fast 🚀    │  │Comprehensive │  │   Browse     │    │
│  │   Free 💰    │  │  Explained   │  │   Files      │    │
│  │  Fragments   │  │  Synthesized │  │   List       │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Comparison

### Performance Metrics

```
┌─────────────────┬──────────────┬─────────────────┬──────────────────┐
│ Tool            │ Speed        │ Token Cost      │ Output Type      │
├─────────────────┼──────────────┼─────────────────┼──────────────────┤
│ search_docs     │ ~1 second    │ 0 tokens        │ Raw fragments    │
│ answer_question │ ~3-5 seconds │ 100-500 tokens  │ AI answer        │
│ list_indexed_   │ <1 second    │ 0 tokens        │ File list        │
└─────────────────┴──────────────┴─────────────────┴──────────────────┘
```

### Use Case Matrix

```
┌────────────────────────────┬──────────────┬─────────────────┐
│ Use Case                   │ Best Tool    │ Alternative     │
├────────────────────────────┼──────────────┼─────────────────┤
│ Find code example          │ search_docs  │ -               │
│ Get config snippet         │ search_docs  │ -               │
│ Quick reference lookup     │ search_docs  │ -               │
│ Find exact quote           │ search_docs  │ -               │
│ Understand workflow        │ answer_q     │ search_docs     │
│ Explain architecture       │ answer_q     │ search_docs     │
│ Troubleshooting steps      │ answer_q     │ search_docs     │
│ Compare approaches         │ answer_q     │ -               │
│ See available docs         │ list_indexed │ -               │
│ Verify indexing            │ list_indexed │ -               │
└────────────────────────────┴──────────────┴─────────────────┘
```

## Decision Flow

```
                    ┌─────────────────────┐
                    │  Need information   │
                    │  from documentation │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ What do you need?   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼────────┐  ┌───▼────┐  ┌───────▼────────┐
    │ Quick lookup     │  │Explain │  │ Browse files   │
    │ Exact text       │  │Synth.  │  │ See what's     │
    │ Code/config      │  │Context │  │ available      │
    └─────────┬────────┘  └───┬────┘  └───────┬────────┘
              │               │                │
    ┌─────────▼────────┐  ┌───▼────────┐  ┌───▼────────┐
    │  search_docs     │  │  answer_   │  │list_indexed│
    │                  │  │  question  │  │   _docs    │
    │ Fast (1s)        │  │ Slow (3-5s)│  │ Instant    │
    │ Free             │  │ Uses tokens│  │ Free       │
    └──────────────────┘  └────────────┘  └────────────┘
```

## Progressive Search Pattern

```
Step 1: Start Fast
┌──────────────────────────────────────┐
│ search_docs(question, max_results=3) │
│                                      │
│ Returns: Document fragments          │
└──────────────┬───────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ Sufficient?  │
        └──────┬───────┘
               │
       ┌───────┴───────┐
       │               │
    Yes│               │No
       │               │
       ▼               ▼
  ┌────────┐    ┌─────────────────────┐
  │ Done ✓ │    │ answer_question()   │
  └────────┘    │                     │
                │ Returns: Full answer│
                └─────────────────────┘
```

## Cost Analysis

### Token Usage Comparison

```
Scenario: "How to deploy this project?"

Option 1: Direct answer_question
┌─────────────────────────────────────┐
│ answer_question()                   │
│ Tokens: ~300                        │
│ Time: 4s                            │
│ Cost: $0.0003 (GPT-4o-mini)        │
└─────────────────────────────────────┘

Option 2: Progressive search
┌─────────────────────────────────────┐
│ 1. search_docs() → Found answer     │
│    Tokens: 0                        │
│    Time: 1s                         │
│    Cost: $0                         │
│                                     │
│ 2. No need for answer_question      │
└─────────────────────────────────────┘

Savings: 100% tokens, 75% time
```

### Monthly Cost Estimate

```
Assumptions:
- 100 queries/day
- 50% can use search_docs
- 50% need answer_question
- Average 300 tokens per answer_question

With Progressive Approach:
┌────────────────────────────────────┐
│ search_docs: 50 queries × $0 = $0  │
│ answer_q: 50 queries × $0.0003 = $0.015/day │
│                                    │
│ Monthly: ~$0.45                    │
└────────────────────────────────────┘

Without Progressive Approach:
┌────────────────────────────────────┐
│ answer_q: 100 queries × $0.0003 = $0.03/day │
│                                    │
│ Monthly: ~$0.90                    │
└────────────────────────────────────┘

Savings: ~50% ($0.45/month)
```

## Output Format Comparison

### search_docs Output

```
🔍 Found 3 relevant document(s):

--- Result 1 ---
📄 Source: docs/deployment.md

To deploy the application:
1. Build: npm run build
2. Test: npm test
3. Deploy: ./deploy.sh

The deployment script handles...
[up to 800 chars per result]

--- Result 2 ---
📄 Source: README.md

## Deployment

Quick deployment guide:
- Ensure all tests pass
- Run deployment script
...

--- Result 3 ---
📄 Source: docs/ci-cd.md
...
```

### answer_question Output

```
The deployment process consists of three main steps:

1. **Build the application**: Run `npm run build` to compile 
   the production bundle. This creates optimized assets in the 
   dist/ directory.

2. **Run tests**: Execute `npm test` to verify all tests pass 
   before deployment. This ensures code quality.

3. **Deploy**: Use the deployment script `./deploy.sh` which 
   handles uploading to the server, running migrations, and 
   restarting services.

The CI/CD pipeline automates this process on every merge to 
the main branch.

📚 Sources:
  • docs/deployment.md
  • README.md
  • docs/ci-cd.md
```

## Best Practices

### ✅ Do

```
✓ Start with search_docs for quick lookups
✓ Use max_results=1-3 for focused search
✓ Use max_results=5-10 for comprehensive search
✓ Switch to answer_question for complex questions
✓ Combine both tools for best results
✓ Read fragments yourself when possible
```

### ❌ Don't

```
✗ Always use answer_question (wastes tokens)
✗ Use max_results=10 for simple lookups
✗ Skip search_docs and go straight to answer_question
✗ Use answer_question for simple fact lookups
✗ Ignore the fragments from search_docs
```

## Real-World Examples

### Example 1: Configuration Lookup

```
❌ Inefficient:
answer_question("What is the database port?")
→ 4s, 200 tokens, $0.0002

✅ Efficient:
search_docs("database port", max_results=1)
→ 1s, 0 tokens, $0
→ Result: "DB_PORT=5432"
```

### Example 2: Architecture Understanding

```
❌ Insufficient:
search_docs("architecture", max_results=3)
→ Returns fragments but no synthesis

✅ Better:
answer_question("Explain the system architecture")
→ Returns synthesized explanation with context
```

### Example 3: Troubleshooting

```
✅ Progressive approach:
1. search_docs("connection error", max_results=3)
   → Quick check for known issues
   
2. If not found:
   answer_question("How to fix connection errors?")
   → Get comprehensive troubleshooting steps
```

## Summary Table

```
┌──────────────┬─────────────┬──────────────┬─────────────┐
│ Aspect       │ search_docs │ answer_q     │list_indexed │
├──────────────┼─────────────┼──────────────┼─────────────┤
│ Speed        │ ⚡⚡⚡       │ ⚡           │ ⚡⚡⚡      │
│ Cost         │ 💰 Free     │ 💰💰💰      │ 💰 Free    │
│ Detail       │ ⭐⭐        │ ⭐⭐⭐⭐⭐  │ ⭐         │
│ Accuracy     │ ⭐⭐⭐⭐⭐  │ ⭐⭐⭐⭐    │ ⭐⭐⭐⭐⭐ │
│ Context      │ ⭐⭐        │ ⭐⭐⭐⭐⭐  │ ⭐         │
│ Best for     │ Quick facts │ Explanations │ Discovery   │
└──────────────┴─────────────┴──────────────┴─────────────┘
```

## Recommendation

**Default strategy**: Start with `search_docs`, escalate to `answer_question` only when needed.

This approach:
- ✅ Minimizes token usage
- ✅ Maximizes speed
- ✅ Provides exact documentation text
- ✅ Allows you to interpret and decide
- ✅ Falls back to AI synthesis when needed

---

For detailed usage patterns, see [AGENT_QUICK_START.md](AGENT_QUICK_START.md)
