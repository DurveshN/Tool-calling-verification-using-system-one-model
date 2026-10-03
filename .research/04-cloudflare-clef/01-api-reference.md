# 01 - API reference (verbatim from sources)

Sources: https://developers.cloudflare.com/workers-ai/models/clef/index.md (fetched raw markdown via curl, 2026-10-03), schema-input.json / schema-output.json at the same path, https://huggingface.co/Cloudflare/clef (README).
No full example RESPONSE body is printed on the Cloudflare model page or blog; none is reproduced here. The only response shape is the output schema below plus the HF description. [Unverified] actual wire output (e.g. exact numeric fields) until a live call is made.

## Model IDs and endpoint
- `@cf/cloudflare/clef` (27B, $0.24 / M input tokens) ; request body `"model": "clef"`
- `@cf/cloudflare/clef-flash` (9B, $0.09 / M input tokens) ; request body `"model": "clef-flash"`
- REST: `POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/cloudflare/clef` with `Authorization: Bearer $CLOUDFLARE_AUTH_TOKEN`
- Binding: `env.AI.run("@cf/cloudflare/clef", {...})` (wrangler `AI` binding; `export interface Env { AI: Ai; }`)
- Note the body requires `model` even though the model ID is in the URL (schema `required: model, state, questions`).

## Parameters (docs text)
- model: "Required. The model selector: "clef" for @cf/cloudflare/clef, "clef-flash" for @cf/cloudflare/clef-flash." pattern `^\s*(clef|clef-flash)\s*$`
- state: "Required. The content to evaluate: a string, or structured data (object/array) such as records, chat logs, or application state. Long text state is truncated to fit the model's token limit."
- questions: "Map of question id to a typed question (noul, choice, or score). 1 to 64 questions; ids may use letters, digits, '_', '.', '-' (max 100 chars). Answers are returned under the same ids."
- images: "Clef extension to the System One API. Optional embedded PNG, JPEG, or WebP images placed before the state (max 4; 4 MiB and 16 megapixels each, 8 MiB total decoded; whole request body max 13 MiB). Remote URLs are not accepted."

## Usage example, Workers binding (verbatim)
```ts
export interface Env {
	AI: Ai;
}

export default {
	async fetch(request, env): Promise<Response> {
		const response = await env.AI.run("@cf/cloudflare/clef", {
			model: "clef",
			state: "Checkout has been failing for every customer for the last hour.",
			questions: {
				urgent: {
					type: "noul",
					instructions: "Is this support request urgent?",
				},
				team: {
					type: "choice",
					instructions: "Which team should handle this request?",
					criteria: {
						billing: "Payments, invoices, and refunds",
						technical: "Outages, errors, and configuration",
						sales: "Plans and upgrades",
					},
				},
				severity: {
					type: "score",
					instructions: "How severe is the customer impact?",
					criteria: ["No impact", "Minor", "Major", "Critical"],
				},
			},
		});

		// response.answers.urgent   -> probability the request is urgent
		// response.answers.team     -> chosen team with per-option probabilities
		// response.answers.severity -> probability-weighted score (0 = lowest level)
		return Response.json(response);
	},
} satisfies ExportedHandler<Env>;
```

## Usage example, curl (verbatim)
```sh
curl https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/ai/run/@cf/cloudflare/clef \
  -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_AUTH_TOKEN" \
  -d '{
    "model": "clef",
    "state": "Checkout has been failing for every customer for the last hour.",
    "questions": {
      "urgent": { "type": "noul", "instructions": "Is this support request urgent?" },
      "team": {
        "type": "choice",
        "instructions": "Which team should handle this request?",
        "criteria": {
          "billing": "Payments, invoices, and refunds",
          "technical": "Outages, errors, and configuration",
          "sales": "Plans and upgrades"
        }
      },
      "severity": {
        "type": "score",
        "instructions": "How severe is the customer impact?",
        "criteria": ["No impact", "Minor", "Major", "Critical"]
      }
    }
  }'
```

## Usage example, Python requests (verbatim)
```py
import os
import requests

ACCOUNT_ID = "your-account-id"
AUTH_TOKEN = os.environ.get("CLOUDFLARE_AUTH_TOKEN")

response = requests.post(
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/cloudflare/clef",
    headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
    json={
        "model": "clef",
        "state": "Checkout has been failing for every customer for the last hour.",
        "questions": {
            "urgent": {
                "type": "noul",
                "instructions": "Is this support request urgent?",
            },
            "team": {
                "type": "choice",
                "instructions": "Which team should handle this request?",
                "criteria": {
                    "billing": "Payments, invoices, and refunds",
                    "technical": "Outages, errors, and configuration",
                    "sales": "Plans and upgrades",
                },
            },
            "severity": {
                "type": "score",
                "instructions": "How severe is the customer impact?",
                "criteria": ["No impact", "Minor", "Major", "Critical"],
            },
        },
    },
)
print(response.json())
```

## HF README: answer shape description (verbatim)
"`systemone` takes a Jev/SystemOne `POST /v1/systemone` request body and returns the same response body: `model`, `answers` keyed by question ID, and `usage`. A `choice` answer has `choice`, `confidence`, and `probabilities`; a `score` answer has the expected `score`, `confidence`, `legend`, and `probabilities`; a `noul` answer has the probability of true. `instructions` is optional, and `images` and `videos` may be added to the request."
(Discrepancy: HF says `instructions` optional, with the question ID used when omitted; the Cloudflare input schema marks `instructions` required. Follow the Cloudflare schema.)
HF also lists `videos` as input; the Cloudflare schema has only `images`. Cloudflare page says it "reads the state as text, JSON, images, or video".

## Input JSON schema (verbatim schema-input.json, pretty-printed)
```json
{
    "type": "object",
    "properties": {
        "model": {
            "type": "string",
            "pattern": "^\\s*(clef|clef-flash)\\s*$",
            "description": "Required. The model selector: \"clef\" for @cf/cloudflare/clef, \"clef-flash\" for @cf/cloudflare/clef-flash."
        },
        "state": {
            "description": "Required. The content to evaluate: a string, or structured data (object/array) such as records, chat logs, or application state. Long text state is truncated to fit the model's token limit."
        },
        "questions": {
            "type": "object",
            "description": "Map of question id to a typed question (noul, choice, or score). 1 to 64 questions; ids may use letters, digits, '_', '.', '-' (max 100 chars). Answers are returned under the same ids.",
            "minProperties": 1,
            "maxProperties": 64,
            "additionalProperties": {
                "oneOf": [
                    {
                        "type": "object",
                        "title": "Noul",
                        "description": "A yes/no question. Returns the probability the answer is yes.",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": [
                                    "noul"
                                ]
                            },
                            "instructions": {
                                "description": "Required. The yes/no question to evaluate: a non-empty string, or an object/array that holds the question in one field and referenced data in others."
                            },
                            "criteria": {
                                "type": "object",
                                "description": "Optional descriptions of what a yes and a no mean.",
                                "properties": {
                                    "true": {
                                        "description": "What a yes (value near 1) means."
                                    },
                                    "false": {
                                        "description": "What a no (value near 0) means."
                                    }
                                }
                            }
                        },
                        "required": [
                            "type",
                            "instructions"
                        ]
                    },
                    {
                        "type": "object",
                        "title": "Choice",
                        "description": "Pick one option from a set you define. Returns the chosen option, a probability per option, and confidence.",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": [
                                    "choice"
                                ]
                            },
                            "instructions": {
                                "description": "Required. What the model should decide: a non-empty string, or an object/array holding the question and referenced data."
                            },
                            "criteria": {
                                "type": "object",
                                "description": "Map of option id (non-empty string) to its description: string, object, array, or null when no detail is needed. 2 to 255 options.",
                                "additionalProperties": {}
                            }
                        },
                        "required": [
                            "type",
                            "instructions",
                            "criteria"
                        ]
                    },
                    {
                        "type": "object",
                        "title": "Score",
                        "description": "Rate the state on an ordered rubric. Returns a probability-weighted score, a probability per level, and confidence.",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": [
                                    "score"
                                ]
                            },
                            "instructions": {
                                "description": "Required. What the model should rate: a non-empty string, or an object/array holding the question and referenced data."
                            },
                            "criteria": {
                                "type": "array",
                                "description": "Ordered level descriptions (string, object, or array), lowest first; levels are indexed from 0. 2 to 10 levels.",
                                "minItems": 2,
                                "maxItems": 10,
                                "items": {}
                            }
                        },
                        "required": [
                            "type",
                            "instructions",
                            "criteria"
                        ]
                    }
                ]
            }
        },
        "images": {
            "type": "array",
            "description": "Clef extension to the System One API. Optional embedded PNG, JPEG, or WebP images placed before the state (max 4; 4 MiB and 16 megapixels each, 8 MiB total decoded; whole request body max 13 MiB). Remote URLs are not accepted.",
            "maxItems": 4,
            "items": {
                "anyOf": [
                    {
                        "type": "string",
                        "title": "Data URL",
                        "description": "A base64 data URL: data:image/png;base64,..., data:image/jpeg;base64,..., or data:image/webp;base64,...",
                        "pattern": "^[Dd][Aa][Tt][Aa]:"
                    },
                    {
                        "type": "object",
                        "title": "Base64 image",
                        "properties": {
                            "content_type": {
                                "type": "string",
                                "description": "image/png, image/jpeg, or image/webp."
                            },
                            "base64": {
                                "type": "string",
                                "description": "Base64-encoded image bytes."
                            }
                        },
                        "required": [
                            "content_type",
                            "base64"
                        ]
                    }
                ]
            }
        }
    },
    "required": [
        "model",
        "state",
        "questions"
    ]
}
```

## Output JSON schema (verbatim schema-output.json, pretty-printed)
```json
{
    "type": "object",
    "contentType": "application/json",
    "properties": {
        "model": {
            "type": "string",
            "description": "The model that performed the evaluation."
        },
        "answers": {
            "type": "object",
            "description": "One answer per question, keyed by the question ids from the request.",
            "additionalProperties": {
                "oneOf": [
                    {
                        "type": "object",
                        "title": "Noul answer",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": [
                                    "noul"
                                ]
                            },
                            "noul": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Probability the answer is yes."
                            }
                        },
                        "required": [
                            "type",
                            "noul"
                        ]
                    },
                    {
                        "type": "object",
                        "title": "Choice answer",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": [
                                    "choice"
                                ]
                            },
                            "choice": {
                                "type": "string",
                                "description": "The highest-probability option."
                            },
                            "probabilities": {
                                "type": "object",
                                "description": "Probability per option/level; values sum to 1.",
                                "additionalProperties": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1
                                }
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "How certain the model is, derived from the probabilities."
                            }
                        },
                        "required": [
                            "type",
                            "choice",
                            "probabilities",
                            "confidence"
                        ]
                    },
                    {
                        "type": "object",
                        "title": "Score answer",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": [
                                    "score"
                                ]
                            },
                            "score": {
                                "type": "number",
                                "description": "Probability-weighted level; can land between levels."
                            },
                            "legend": {
                                "type": "object",
                                "description": "Level index (string) mapped to its description.",
                                "additionalProperties": {}
                            },
                            "probabilities": {
                                "type": "object",
                                "description": "Probability per option/level; values sum to 1.",
                                "additionalProperties": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1
                                }
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "How certain the model is, derived from the probabilities."
                            }
                        },
                        "required": [
                            "type",
                            "score",
                            "legend",
                            "probabilities",
                            "confidence"
                        ]
                    }
                ]
            }
        },
        "usage": {
            "type": "object",
            "properties": {
                "input_tokens": {
                    "type": "integer"
                },
                "output_tokens": {
                    "type": "integer"
                }
            },
            "required": [
                "input_tokens",
                "output_tokens"
            ]
        }
    },
    "required": [
        "model",
        "answers",
        "usage"
    ]
}
```
