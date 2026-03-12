# VerseFina Internal Style Guide

## Highest Rule
Existing code wins over this document, and this document wins over model improvisation.

## Python Example
Good:
```python
from pydantic import BaseModel, Field


class AgentSnapshot(BaseModel):
    agent_id: str = Field(..., description="Globally unique agent id")
    equity: float = Field(..., ge=0, description="Current total equity")
```

Bad:
```python
class agent_data:
    def __init__(self, id):
        self.id = id
```

## React Example
Good:
```tsx
'use client';

import { useQuery } from '@tanstack/react-query';

export default function AgentPage({ params }: { params: { agentId: string } }) {
  return <div>{params.agentId}</div>;
}
```

## Execution Notes
- Reuse current folder structure before adding new modules.
- Prefer extending existing schemas and services over introducing parallel abstractions.
- Keep commits small and focused.
