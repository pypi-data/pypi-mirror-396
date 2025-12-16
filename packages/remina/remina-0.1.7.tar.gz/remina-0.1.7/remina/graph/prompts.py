"""
Prompts for entity and relationship extraction.
"""

ENTITY_EXTRACTION_PROMPT = """You are an entity extraction system. Extract named entities from the conversation.

## Entity Extraction Rules

1. **Speaker Extraction**: If the text is a conversation (contains "User:" or similar), extract the speaker as an entity.
2. **Pronoun Resolution**: When possible, resolve pronouns (I, my, me) to "User" entity.
3. **Full Names**: Use full names when available (e.g., "John Smith" not just "John").

## Entity Types
- person: People, users, individuals
- company: Companies, organizations, teams
- technology: Programming languages, tools, frameworks
- place: Cities, countries, locations
- product: Products, services
- concept: Abstract ideas, topics, preferences
- other: Anything else significant

For each entity, provide:
- name: The entity name (proper noun, normalized)
- type: One of the types above
- summary: Brief description based on context (1 sentence max)

Rules:
1. Extract specific, named entities only (not generic terms like "the company")
2. Normalize names (e.g., "John" and "John Smith" referring to same person = "John Smith")
3. Include entities mentioned by any speaker
4. Maximum {max_entities} entities

Respond with JSON only:
{{
    "entities": [
        {{"name": "User", "type": "person", "summary": "The user in the conversation"}},
        {{"name": "John Smith", "type": "person", "summary": "The user's name"}},
        {{"name": "Acme Corp", "type": "company", "summary": "John's employer"}}
    ]
}}

Conversation:
{content}"""


RELATIONSHIP_EXTRACTION_PROMPT = """You are a relationship extraction system. Given entities and conversation, extract relationships between them.

Known entities:
{entities}

## Relationship Types (use SCREAMING_SNAKE_CASE)

Identity:
- HAS_NAME, IS_NAMED, CALLED

Location:
- LIVES_IN, LOCATED_IN, FROM

Work:
- WORKS_AT, EMPLOYED_BY, JOB_IS

Preferences:
- LIKES, LOVES, PREFERS, DISLIKES, HATES

Social:
- KNOWS, FRIENDS_WITH, MARRIED_TO

Ownership:
- OWNS, HAS, USES

General:
- RELATED_TO, IS_A, PART_OF

For each relationship, provide:
- source: Source entity name (must be from the list above)
- target: Target entity name (must be from the list above)
- relation_type: Relationship type in SCREAMING_SNAKE_CASE
- fact: Human-readable fact sentence that can be understood without context

Rules:
1. Only use entities from the provided list
2. Each relationship should be a clear fact from the conversation
3. The "fact" field should be a standalone statement
4. Avoid duplicate or redundant relationships
5. Maximum {max_relationships} relationships

## Examples

Input: "My name is John"
Output:
{{
    "relationships": [
        {{"source": "User", "target": "John", "relation_type": "HAS_NAME", "fact": "The user's name is John"}}
    ]
}}

Input: "I love TypeScript"
Output:
{{
    "relationships": [
        {{"source": "User", "target": "TypeScript", "relation_type": "LOVES", "fact": "The user loves TypeScript"}}
    ]
}}

Respond with JSON only:
{{
    "relationships": [
        {{
            "source": "User",
            "target": "John Smith",
            "relation_type": "HAS_NAME",
            "fact": "The user's name is John Smith"
        }},
        {{
            "source": "User",
            "target": "Acme Corp",
            "relation_type": "WORKS_AT",
            "fact": "The user works at Acme Corp"
        }}
    ]
}}

Conversation:
{content}"""


ENTITY_DEDUP_PROMPT = """You are an entity deduplication system. Determine if two entities refer to the same real-world entity.

Entity A: {entity_a}
Entity B: {entity_b}

Consider:
- Name variations (John vs John Smith)
- Abbreviations (IBM vs International Business Machines)
- Context clues

Respond with JSON only:
{{
    "is_same": true/false,
    "confidence": 0.0-1.0,
    "canonical_name": "preferred name if same entity"
}}"""
