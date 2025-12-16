# Application Specification Templates

This directory contains ready-to-use application specification templates for the Autonomous Coding Agent.

## Available Templates

| Template | Description | Complexity | Estimated Features |
|----------|-------------|------------|-------------------|
| `task_manager_spec.txt` | Full-featured task management app like Todoist/Linear | High | 150-200 |
| `ecommerce_spec.txt` | E-commerce platform with cart, checkout, admin | High | 150-200 |

## How to Use a Template

### Option 1: Copy to Prompts Directory

```bash
# Copy the template to use it
cp templates/task_manager_spec.txt prompts/app_spec.txt

# Run the agent
python autonomous_agent_demo.py --project-dir ./my_task_app
```

### Option 2: Reference Directly

Modify `prompts.py` to load from a different location, or symlink:

```bash
ln -sf ../templates/task_manager_spec.txt prompts/app_spec.txt
```

## Customizing Templates

### Reducing Scope for Faster Demos

Edit `prompts/initializer_prompt.md` and change the feature count:

```markdown
# Original (full build - many hours)
Based on `app_spec.txt`, create a file called `feature_list.json` with 200 detailed...

# Reduced (faster demo - 1-2 hours)
Based on `app_spec.txt`, create a file called `feature_list.json` with 50 detailed...
```

### Key Sections to Customize

1. **`<overview>`**: Describe your unique value proposition
2. **`<technology_stack>`**: Change frameworks if needed
3. **`<core_features>`**: Add/remove features
4. **`<database_schema>`**: Adjust data model
5. **`<design_system>`**: Change colors, fonts, spacing
6. **`<implementation_steps>`**: Reorder priorities

## Creating Your Own Template

Start with this structure:

```xml
<project_specification>
  <project_name>Your App Name</project_name>
  
  <overview>
    2-3 sentences describing what you're building and why.
  </overview>
  
  <technology_stack>
    <!-- Define your tech choices -->
  </technology_stack>
  
  <core_features>
    <!-- List all features in detail -->
  </core_features>
  
  <database_schema>
    <!-- Define all tables and fields -->
  </database_schema>
  
  <api_endpoints_summary>
    <!-- List all API endpoints -->
  </api_endpoints_summary>
  
  <ui_layout>
    <!-- Describe page layouts -->
  </ui_layout>
  
  <design_system>
    <!-- Colors, typography, components -->
  </design_system>
  
  <implementation_steps>
    <!-- Phased delivery plan -->
  </implementation_steps>
  
  <success_criteria>
    <!-- How to know when it's done -->
  </success_criteria>
</project_specification>
```

## Tips for Better Specifications

1. **Be Exhaustive**: More detail = better implementation
2. **Include Edge Cases**: Error states, empty states, loading states
3. **Specify Interactions**: Describe how features should feel
4. **Define Testing Steps**: Each feature needs verifiable outcomes
5. **Prioritize Features**: Order by importance for incremental delivery

## Technology Stack Options

### Frontend Frameworks
- React + Vite (recommended)
- Vue 3 + Vite
- Svelte + SvelteKit
- Next.js

### Backend Options
- Node.js + Express (recommended)
- FastAPI (Python)
- Hono (Edge runtime)

### Database Options
- SQLite (recommended for simplicity)
- PostgreSQL
- MongoDB

### Styling Options
- Tailwind CSS (recommended)
- Chakra UI
- shadcn/ui

