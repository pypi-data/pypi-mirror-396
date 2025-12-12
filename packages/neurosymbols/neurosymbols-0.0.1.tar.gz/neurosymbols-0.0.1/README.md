# 🧠 NeuroSymbols: Creating the Deterministic Logic Layer for LLMs

Automatically discover schemas and generate deterministic Prolog rules from unstructured text using LLMs. Build reliable, verifiable logic layers that transform unstructured data into structured validation rules.

NeuroSymbols performs **double induction**:

1. **Structure Induction**: Discovers Pydantic schemas from unstructured text
2. **Logic Induction**: Generates Prolog rules from structured data examples

## ✨ What It Does

Instead of manually crafting schemas and validation rules, NeuroSymbols uses LLMs to automatically discover the structure and logic needed to validate your data. Just provide examples of valid and invalid text, and watch the system learn both the schema and the rules.

## 🎯 Quick Start

```python
from neurosymbols import NeurosymbolicPipeline

# Provide unstructured text examples with validity labels
raw_training_data = [
    {"text": "User John is 25 years old and his account is active.", "valid": True},
    {"text": "Sarah is 40 years old, current status is active.", "valid": True},
    {"text": "Mike is 16 years old, account is active.", "valid": False},  # Too young
    {"text": "Emily is 30, but her account is suspended.", "valid": False},  # Wrong status
]

# Initialize pipeline
pipeline = NeurosymbolicPipeline(
    model_id="gpt-4o",
    verbose=True,
)

# Train - automatically discovers schema and rules
pipeline.train(raw_training_data)

# Predict on new text
result = pipeline.predict("Mark is 50 years old and active.")
print(f"Valid: {result}")  # True
```

## 📦 Installation

```bash
pip install neurosymbols
```

Or with `uv`:

```bash
uv pip install neurosymbols
```

## 🌟 Key Features

* **Double Induction**: Automatically discovers both schema and logic rules
* **Zero Manual Configuration**: No need to define schemas or rules upfront
* **Domain Adaptation**: Automatically adapts to different domains (banking, healthcare, etc.)
* **Pydantic Integration**: Works seamlessly with Pydantic models
* **Prolog Rules**: Generates deterministic, verifiable Prolog logic
* **Case Descriptions**: Provide business context to guide discovery
* **Flexible Training**: Use existing schemas or rules, or discover everything

## 📚 Examples

### Basic Pipeline

The simplest use case - let the system discover everything:

```python
from neurosymbols import NeurosymbolicPipeline

raw_training_data = [
    {"text": "User John is 25 years old and his account is active.", "valid": True},
    {"text": "Sarah is 40 years old, current status is active.", "valid": True},
    {"text": "Mike is 16 years old, account is active.", "valid": False},
    {"text": "Emily is 30, but her account is suspended.", "valid": False},
]

pipeline = NeurosymbolicPipeline(model_id="gpt-4o", verbose=True)
pipeline.train(raw_training_data)

# Test
result = pipeline.predict("Mark is 50 years old and active.")
print(f"Valid: {result}")  # True
```

### With Existing Schema

If you already have a Pydantic model, skip schema discovery:

```python
from pydantic import BaseModel, Field
from neurosymbols import NeurosymbolicPipeline

class User(BaseModel):
    age: int = Field(..., description="User age in years")
    status: str = Field(..., description="Account status: 'active' or 'suspended'")

raw_training_data = [
    {"text": "User John is 25 years old and his account is active.", "valid": True},
    {"text": "Mike is 16 years old, account is active.", "valid": False},
]

pipeline = NeurosymbolicPipeline(model_id="gpt-4o")
pipeline.train(raw_training_data, schema=User)  # Only induces rules
```

### With Existing Rules

If you have both schema and rules, skip discovery and induction:

```python
from pydantic import BaseModel, Field
from neurosymbols import NeurosymbolicPipeline

class User(BaseModel):
    age: int = Field(..., description="User age in years")
    status: str = Field(..., description="Account status: 'active' or 'suspended'")

existing_rule = "valid(X) :- age(X, A), A >= 18, status(X, 'active')."

raw_training_data = [
    {"text": "User John is 25 years old and his account is active.", "valid": True},
]

pipeline = NeurosymbolicPipeline(model_id="gpt-4o")
pipeline.train(raw_training_data, schema=User, prolog_rule=existing_rule)
```

### With Case Description

Provide business context to guide discovery:

```python
from neurosymbols import NeurosymbolicPipeline

case_description = """
Banking Transaction Validation Rules:
- Transactions to certain countries (Russia, North Korea, Iran) are restricted
- High-value transactions (>$50,000) to restricted countries are always invalid
- Transactions to approved countries (United States, US, Canada) are generally valid
"""

raw_training_data = [
    {"text": "Transfer of $500 to United States account", "valid": True},
    {"text": "Transaction of $50,000 to Russia", "valid": False},
    {"text": "Wire transfer of $75,000 to North Korea", "valid": False},
]

pipeline = NeurosymbolicPipeline(model_id="gpt-4o", verbose=True)
pipeline.train(raw_training_data, case_description=case_description)
```

### Manual Setup

For full control, set schema and rules manually:

```python
from pydantic import BaseModel, Field
from neurosymbols import NeurosymbolicPipeline

class User(BaseModel):
    age: int = Field(..., description="User age in years")
    status: str = Field(..., description="Account status: 'active' or 'suspended'")

pipeline = NeurosymbolicPipeline(model_id="gpt-4o")

# Manually set schema
pipeline.set_schema(User)

# Manually set Prolog rule
rule = "valid(X) :- age(X, A), A >= 18, status(X, 'active')."
pipeline.set_prolog_rule(rule)

# Now use for prediction
result = pipeline.predict("Mark is 50 years old and active.")
```

### Training Rules from Schema

Train Prolog rules from an existing Pydantic model:

```python
from pydantic import BaseModel, Field
from neurosymbols import NeurosymbolicPipeline

class User(BaseModel):
    age: int = Field(..., description="User age in years")
    status: str = Field(..., description="Account status: 'active' or 'suspended'")

raw_training_data = [
    {"text": "User John is 25 years old and his account is active.", "valid": True},
    {"text": "Mike is 16 years old, account is active.", "valid": False},
]

pipeline = NeurosymbolicPipeline(model_id="gpt-4o", verbose=True)
pipeline.train_rules_from_schema(User, raw_training_data)
```

## 🔄 How It Works

The pipeline performs **double induction**:

1. **Structure Induction** (if schema not provided):
   - Analyzes unstructured text examples
   - Discovers common fields and data types
   - Generates a Pydantic-compatible schema

2. **Data Extraction**:
   - Extracts structured data from text using the schema
   - Validates with Pydantic models

3. **Logic Induction** (if rule not provided):
   - Analyzes structured examples with validity labels
   - Generates Prolog rules that distinguish valid from invalid
   - Creates deterministic, verifiable logic

4. **Prediction**:
   - Extracts structured data from new text
   - Validates using Prolog rules
   - Returns boolean result

## 📖 API Reference

### `NeurosymbolicPipeline`

Main pipeline class for neuro-symbolic double induction.

**Parameters:**

* `model_id` (str): LLM model identifier (default: "gpt-4.1-mini")
* `api_key` (str | None): API key for the LLM (default: from environment)
* `api_base` (str | None): API base URL (for Azure OpenAI or custom endpoints)
* `api_version` (str | None): API version (for Azure OpenAI)
* `lm` (dspy.LM | None): Optional DSPy language model instance (overrides model_id/api_key)
* `verbose` (bool): Print progress information during training and prediction (default: False)

**Methods:**

#### `train(raw_examples, schema=None, prolog_rule=None, case_description=None)`

Train the pipeline on unstructured text examples.

**Parameters:**

* `raw_examples` (list[dict[str, Any]]): List of dicts with 'text' (str) and 'valid' (bool) keys
* `schema` (SchemaDefinition | type[BaseModel] | None): Optional pre-existing schema. If None, schema will be discovered from examples.
* `prolog_rule` (str | None): Optional pre-existing Prolog rule string. If None, rule will be induced from structured data.
* `case_description` (str | None): Optional business context and domain knowledge to guide schema discovery and rule creation.

#### `train_rules_from_schema(model, raw_examples, case_description=None)`

Train Prolog rules from an existing Pydantic model.

**Parameters:**

* `model` (type[BaseModel]): Pydantic model class to use for extraction
* `raw_examples` (list[dict[str, Any]]): List of dicts with 'text' (str) and 'valid' (bool) keys
* `case_description` (str | None): Optional business context to guide rule creation

#### `set_schema(schema)`

Manually set the schema for the pipeline.

**Parameters:**

* `schema` (SchemaDefinition | type[BaseModel]): SchemaDefinition or Pydantic model class

#### `set_prolog_rule(rule)`

Manually set the Prolog rule for the pipeline.

**Parameters:**

* `rule` (str): Prolog rule string

#### `predict(new_text)`

Predict validity of new unstructured text.

**Parameters:**

* `new_text` (str): Raw text input to evaluate

**Returns:**

* `bool`: True if the text is valid according to learned rules, False otherwise

**Raises:**

* `ValueError`: If pipeline hasn't been trained yet

## 🎓 Use Cases

* **Data Validation**: Automatically learn validation rules from examples
* **Domain Adaptation**: Quickly adapt to new domains without code changes
* **Rule Discovery**: Discover business rules from labeled examples
* **Schema Discovery**: Automatically identify data structures from text
* **Deterministic Logic**: Generate verifiable, deterministic validation logic

## 🔧 Requirements

* Python >= 3.11
* dspy >= 3.0.0
* pydantic >= 2.0.0
* pyswip >= 0.2.10

## 📝 License

MIT

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 🔗 Related Projects

* [DSPy](https://github.com/stanfordnlp/dspy) - Framework for programming with foundation models
* [Pydantic](https://github.com/pydantic/pydantic) - Data validation using Python type annotations
* [PySwip](https://github.com/yuce/pyswip) - Python-SWI-Prolog bridge
