# AI-Powered Media Recommendations

This feature uses LLMs to generate personalized daily recommendations from your Emby and Booklore collections.

## How It Works

The recommendation system generates **two types of recommendations** for each category (books and videos):

1. **Pattern-Based Recommendations** (default: 5 per category)
   - Analyzes your collection's genres, authors, themes, and patterns
   - Recommends new items that align with your existing tastes
   - Helps you discover more of what you already love

2. **Surprise Recommendation** (1 per category)
   - Intentionally steps outside your comfort zone
   - Introduces new genres, styles, or perspectives
   - Helps diversify and expand your collection

**Total Output**: With `count=5`, you get 6 book recommendations + 6 video recommendations = **12 total recommendations**

## Setup

### 1. Configure LLM Provider

Add the following to your `.env` file:

```bash
# LLM Configuration
LLM_PROVIDER=openai  # Any name for documentation
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=  # Optional: custom base URL
LLM_MODEL=gpt-4o-mini
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.7
```

### Supported Providers

The system works with **any OpenAI-compatible API**. Just set `LLM_BASE_URL` to your provider's endpoint.

**OpenAI**
```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_BASE_URL=
LLM_MODEL=gpt-4o-mini
```

**DeepSeek**
```bash
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

**Groq**
```bash
LLM_PROVIDER=groq
LLM_API_KEY=gsk-...
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama3.2-70b-vision-preview
```

**Any OpenAI-Compatible Provider**
```bash
LLM_PROVIDER=custom
LLM_API_KEY=your-key
LLM_BASE_URL=https://your-provider.com/v1
LLM_MODEL=model-name
```

**Anthropic Claude** (uses different API format)
```bash
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-haiku-20241022
```

**Ollama (Local)** (uses different API format)
```bash
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
# No API key needed for Ollama
```

### 2. Home Assistant Integration

You can use the RESTful sensor to display recommendations in Home Assistant:

```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: Daily Media Recommendations
    resource: http://your-collection-helper:8090/recommendations
    method: POST
    headers:
      Content-Type: application/json
    payload: '{"count": 5}'
    value_template: "{{ value_json.recommendations | length }}"
    json_attributes:
      - recommendations
      - date
      - total_items_considered
```

**Note**: With `count=5`, you'll receive 12 total recommendations (6 books + 6 videos).

Then create a card in your dashboard:

```yaml
type: entities
entities:
  - sensor.daily_media_recommendations
```

Or use a custom markdown card to display recommendations by category:

```yaml
type: markdown
content: |
  {% set recommendations = state_attr('sensor.daily_media_recommendations', 'recommendations') %}
  {% set books = recommendations | selectattr('media_type', 'equalto', 'book') | list %}
  {% set videos = recommendations | selectattr('media_type', 'equalto', 'video') | list %}
  ## Daily Recommendations ({{ state_attr('sensor.daily_media_recommendations', 'date')[:10] }})
  ### Books ({{ books | length }})
  {% for rec in books %}
  - **{{ rec.name }}**
    - {{ rec.reason }}
  {% endfor %}
  ### Videos ({{ videos | length }})
  {% for rec in videos %}
  - **{{ rec.name }}**
    - {{ rec.reason }}
  {% endfor %}
```

## API Usage

### Generate Recommendations

```bash
curl -X POST http://localhost:8090/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "count": 5,
    "user_preferences": "I enjoy sci-fi movies and technical books"
  }'
```

**Parameters**:
- `count` (integer, 1-20): Number of pattern-based recommendations **per category** (books and videos). Each category will receive this many recommendations plus 1 surprise recommendation.
- `user_preferences` (string, optional): Additional context to guide recommendations

### Response Format

```json
{
  "date": "2026-01-01T12:00:00",
  "recommendations": [
    {
      "name": "Project Hail Mary",
      "source": "suggested_book",
      "media_type": "book",
      "reason": "This modern sci-fi classic aligns with your interest in speculative fiction",
      "match_score": 0.90
    },
    {
      "name": "Maus",
      "source": "suggested_book",
      "media_type": "book",
      "reason": "To diversify your collection, this Pulitzer Prize-winning graphic novel memoir introduces visual storytelling and historical depth",
      "match_score": 0.75
    },
    {
      "name": "Nirvana in Fire",
      "source": "suggested_video",
      "media_type": "video",
      "reason": "This historical political drama perfectly matches your appreciation for intricate plots and strategy",
      "match_score": 0.98
    },
    {
      "name": "Arcane",
      "source": "suggested_video",
      "media_type": "video",
      "reason": "This surprise recommendation diversifies your collection with animated storytelling while maintaining the complex world-building you enjoy",
      "match_score": 0.75
    }
  ],
  "total_items_considered": 680,
  "llm_provider": "openai"
}
```

**Note**: Surprise recommendations typically have lower `match_score` values (around 0.75) because they intentionally step outside your collection patterns.

## Recommendation Process

1. **Fetch**: Retrieves all items from Emby and Booklore
2. **Separate**: Splits items by category (books vs videos)
3. **Analyze**: Sends each category separately to the LLM for pattern analysis
4. **Generate**:
   - Creates N recommendations based on your collection's patterns
   - Adds 1 surprise recommendation per category to diversify your collection
5. **Return**: Provides ranked recommendations with reasons and match scores

## Customization

You can provide user preferences to guide recommendations:

```json
{
  "count": 3,
  "user_preferences": "I'm in the mood for something light and funny today. Prefer TV series over movies."
}
```

This will generate:
- 3 pattern-based book recommendations + 1 surprise book recommendation
- 3 pattern-based video recommendations + 1 surprise video recommendation
- **Total: 8 recommendations** (4 books + 4 videos)

## Cost Considerations

- **OpenAI gpt-4o-mini**: ~$0.01-0.02 per recommendation request (generates 12 total recommendations with count=5)
- **Anthropic Haiku**: ~$0.0025-0.005 per recommendation request
- **Ollama**: Free (runs locally)

The system samples up to 30 items per category for analysis to keep token usage reasonable while maintaining recommendation quality.

## Tips for Best Results

1. **Regular Updates**: Run recommendations daily or weekly to discover new content
2. **Provide Context**: Use `user_preferences` for mood-based recommendations
3. **Embrace Surprises**: The surprise recommendations help expand your horizons - give them a try!
4. **Adjust Count**: Lower `count` (e.g., 3) for quicker, more focused recommendations
5. **Review Scores**: Higher `match_score` indicates stronger alignment with your current collection
