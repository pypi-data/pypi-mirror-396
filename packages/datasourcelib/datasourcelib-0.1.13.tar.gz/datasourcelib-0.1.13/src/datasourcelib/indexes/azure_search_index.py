from typing import List, Dict, Any, Optional
from datasourcelib.utils.logger import get_logger

logger = get_logger(__name__)

class AzureSearchIndexer:
    """
    Azure Cognitive Search indexer with vector search support.
    Required vector_db_config:
      - aisearch_endpoint: str
      - aisearch_index_name: str
      - aisearch_api_key

    Optional vector search config:
      - vectorization: bool (enable vector search)
      - vector_config: dict
        - dimensions: int (default 1024)
        - algorithm: str ('hnsw' or 'flat', default 'hnsw')
        - metric: str ('cosine', 'euclidean', 'dotProduct', default 'cosine')
      - key_field: str (default 'id')
      - vector_field: str (default 'contentVector')
      - embedding_endpoint: str (Azure OpenAI endpoint for embeddings)
      - embedding_key: str (Azure OpenAI API key)
      - embedding_deployment: str (Azure OpenAI model deployment name)

    Semantic configuration (optional):
      - semantic_configuration: dict with optional keys:
          - name: str (name of semantic config)
          - title_field: str (field name to use as title)
          - content_field: str (field name to use as content)
          - prioritized_content_fields: List[str]
          - keywords_field: str
          - default: bool (set as default config if True)
    """

    def __init__(self, vector_db_config: Dict[str, Any]):
        self.config = vector_db_config or {}
        self._client = None
        self._index_client = None
        self._embedding_client = None

    def validate_config(self) -> bool:
        required = ("aisearch_endpoint", "aisearch_index_name", "aisearch_api_key")
        missing = [k for k in required if k not in self.config]
        
        # Check vector search requirements if enabled
        if self.config.get("vectorization", False):
            vector_required = ("embedding_endpoint", "embedding_key", "embedding_deployment")
            missing.extend([k for k in vector_required if k not in self.config])
        
        if missing:
            logger.error("AzureSearchIndexer.validate_config missing: %s", missing)
            return False
        return True

    def _ensure_sdk(self):
        try:
            from azure.core.credentials import AzureKeyCredential  # type: ignore
            from azure.search.documents import SearchClient  # type: ignore
            from azure.search.documents.indexes import SearchIndexClient  # type: ignore
            from openai import AzureOpenAI # type: ignore
            from azure.search.documents.indexes.models import (
                SearchIndex,
                SearchField,
                SearchFieldDataType,
                SimpleField,
                SearchableField,
                VectorSearch,
                VectorSearchProfile,
                HnswAlgorithmConfiguration,
                # semantic models (optional; present in recent SDKs)
                SemanticSearch,
                SemanticField,
                SemanticConfiguration,
                SemanticPrioritizedFields
            ) # type: ignore

        except Exception as e:
            raise RuntimeError("Required packages missing. Install: azure-search-documents openai") from e

        return (
            AzureKeyCredential, SearchClient, SearchIndexClient, AzureOpenAI, SearchIndex, SearchField,
            SearchFieldDataType, SimpleField, SearchableField, VectorSearch, VectorSearchProfile,
            HnswAlgorithmConfiguration, SemanticSearch, SemanticField, SemanticConfiguration, SemanticPrioritizedFields
        )

    def _setup_embedding_client(self):
        if not self._embedding_client and self.config.get("vectorization"):
            try:
                AzureKeyCredential, SearchClient, SearchIndexClient, AzureOpenAI, SearchIndex, SearchField, SearchFieldDataType, SimpleField, SearchableField, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration, SemanticSearch, SemanticField, SemanticConfiguration, SemanticPrioritizedFields = self._ensure_sdk()
                self._embedding_client = AzureOpenAI(
                    api_version=self.config["embedding_api_version"],
                    azure_endpoint=self.config["embedding_endpoint"],
                    api_key=self.config["embedding_key"],
                )
                logger.info("Azure OpenAI embedding client initialized")
            except Exception as ex:
                logger.exception("Failed to initialize embedding client")
                raise

    def _get_embeddings(self, text: str) -> List[float]:
        try:
            self._setup_embedding_client()
            response = self._embedding_client.embeddings.create(
                model=self.config["embedding_deployment"],
                input=text
            )
            return response.data[0].embedding
        except Exception as ex:
            logger.exception(f"Failed to get embeddings for text: {text[:100]}...")
            raise

    def _build_vector_search_config_old(self):
        AzureKeyCredential, SearchClient, SearchIndexClient, AzureOpenAI, SearchIndex, SearchField, SearchFieldDataType, SimpleField, SearchableField, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration, SemanticSearch, SemanticField, SemanticConfiguration, SemanticPrioritizedFields = self._ensure_sdk()
        vector_config = self.config.get("vector_config", {})
        dimensions = vector_config.get("dimensions", 1536)

        vector_search = VectorSearch(
                profiles=[VectorSearchProfile(name="vector-profile-1", algorithm_configuration_name="algorithms-config-1")],
                algorithms=[HnswAlgorithmConfiguration(name="algorithms-config-1")]
            )

        return vector_search, dimensions
    
    def _build_vector_search_config(self):
        AzureKeyCredential, SearchClient, SearchIndexClient, AzureOpenAI, SearchIndex, SearchField, SearchFieldDataType, SimpleField, SearchableField, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration, SemanticSearch, SemanticField, SemanticConfiguration, SemanticPrioritizedFields = self._ensure_sdk()

        vector_config = self.config.get("vector_config", {})
        dimensions = vector_config.get("dimensions", 1536)
        algorithm = vector_config.get("algorithm", "hnsw").lower()

        # Build algorithm configuration (SDK model if available)
        alg_cfg = HnswAlgorithmConfiguration(name="algorithms-config-1")

        # Build vectorizer settings using Azure OpenAI config from vector_db_config
        deployment = self.config.get("embedding_deployment")
        endpoint = self.config.get("embedding_endpoint")
        api_key = self.config.get("embedding_key")
        # modelName required for API version 2025-09-01 — prefer explicit embedding_model, fall back to deployment
        model_name = self.config.get("embedding_model") or deployment
        content_field = self.config.get("content_field", "content")
        vector_field = self.config.get("vector_field", "contentVector")

        if not model_name:
            raise RuntimeError("Vectorizer configuration requires 'embedding_model' or 'embedding_deployment' in vector_db_config")

        # Define vectorizer with explicit name and required azureOpenAIParameters including modelName
        vectorizer_name = "azure-openai-vectorizer"
        vectorizer = {
            "name": vectorizer_name,
            "kind": "azureOpenAI",
            "azureOpenAIParameters": {
                "resourceUri": endpoint.rstrip('/') if endpoint else None,
                # include both modelName (required) and deploymentId (if provided)
                "modelName": model_name,
                **({"deploymentId": deployment} if deployment else {}),
                "apiKey": api_key
            },
            "options": {
                "fieldMapping": [
                    {
                        "sourceContext": f"/document/{content_field}",
                        "outputs": [
                            {
                                "targetContext": f"/document/{vector_field}",
                                "targetDimensions": dimensions
                            }
                        ]
                    }
                ]
            }
        }

        profile_name = "vector-profile-1"
        try:
            # Create profile with vectorizer reference (SDK may expect vectorizer_name or vectorizer depending on version)
            try:
                profile = VectorSearchProfile(
                    name=profile_name,
                    algorithm_configuration_name="algorithms-config-1",
                    vectorizer_name=vectorizer_name
                )
            except TypeError:
                # fallback if SDK constructor uses different parameter names
                profile = VectorSearchProfile(name=profile_name, algorithm_configuration_name="algorithms-config-1")
                try:
                    setattr(profile, "vectorizer_name", vectorizer_name)
                except Exception:
                    pass

            try:
                # Construct full vector search config with both profile and vectorizer
                vector_search = VectorSearch(
                    profiles=[profile],
                    algorithms=[alg_cfg],
                    vectorizers=[vectorizer]
                )
            except Exception:
                # Fallback to dict if SDK constructor differs
                vector_search = {
                    "profiles": [{
                        "name": profile_name,
                        "algorithmConfigurationName": "algorithms-config-1",
                        "vectorizerName": vectorizer_name
                    }],
                    "algorithms": [{"name": "algorithms-config-1"}],
                    "vectorizers": [vectorizer]
                }
        except Exception:
            # Full dict fallback
            vector_search = {
                "profiles": [{
                    "name": profile_name,
                    "algorithmConfigurationName": "algorithms-config-1",
                    "vectorizerName": vectorizer_name
                }],
                "algorithms": [{"name": "algorithms-config-1"}],
                "vectorizers": [vectorizer]
            }

        logger.info("Built vector_search config (dimensions=%s, model=%s, vectorizer=%s)",
                    dimensions, model_name, vectorizer_name)
        return vector_search, dimensions


    def _build_semantic_settings(self):
        """
        Build semantic settings from configuration. Returns either an SDK SemanticSettings
        instance (preferred) or a plain dict fallback that can be passed to SearchIndex.
        """
        AzureKeyCredential, SearchClient, SearchIndexClient, AzureOpenAI, SearchIndex, SearchField, SearchFieldDataType, SimpleField, SearchableField, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration, SemanticSearch, SemanticField, SemanticConfiguration, SemanticPrioritizedFields = self._ensure_sdk()
        semantic_cfg = self.config.get("semantic_configuration")
        if not semantic_cfg:
            return None

        # Normalize config fields
        name = semantic_cfg.get("name", "semantic-config-1")
        title_field = semantic_cfg.get("title_field")
        #content_field = semantic_cfg.get("content_field")
        prioritized_content = semantic_cfg.get("prioritized_content_fields", [])[0]
        keywords_fields = semantic_cfg.get("keywords_fields",[])[0]
        logger.info(f"Building semantic configuration: title_field={title_field}, keywords_field={keywords_fields}, prioritized_content={prioritized_content}")
        try:
            semantic_config = SemanticConfiguration(
                                name="semantic-config-1",
                                prioritized_fields=SemanticPrioritizedFields(
                                    title_field=SemanticField(field_name=title_field),
                                    keywords_fields=[SemanticField(field_name=keywords_fields)],
                                    content_fields=[SemanticField(field_name=prioritized_content)]
                                )
                            )
                    
        except Exception:
                  return None  # Fallback to dict if SDK classes not available
        return SemanticSearch(configurations=[semantic_config])

    def _infer_field_type(self, value) -> Any:
        #Map Python types to SearchFieldDataType, including collections

        AzureKeyCredential, SearchClient, SearchIndexClient, AzureOpenAI, SearchIndex, SearchField, SearchFieldDataType, SimpleField, SearchableField, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration, SemanticSearch, SemanticField, SemanticConfiguration, SemanticPrioritizedFields = self._ensure_sdk()
        
        if value is None:
            return SearchFieldDataType.String
            
        t = type(value)
        
        # Handle list/array types as Collections
        if t in (list, tuple):
            # If empty list, default to Collection of Double
            if not value:
                return SearchFieldDataType.Collection(SearchFieldDataType.Double)
            # Get type of first element for non-empty lists
            element_type = self._infer_field_type(value[0])
            return SearchFieldDataType.Collection(element_type)
        # Handle vector embeddings (list or tuple of floats)
        if type(value) in (list, tuple) and all(isinstance(x, (int, float)) for x in value):
            return SearchFieldDataType.Collection(SearchFieldDataType.Single)
            
        # Handle basic types
        logger.info(f"######## Infer field type for value:[ {value} ] of type [ {t} ]")
        if t is bool:
            return SearchFieldDataType.Boolean
        if t is int:
            return SearchFieldDataType.Int32
        if t is float:
            return SearchFieldDataType.Double
        print(f"############## Infer field type for value: {value} of type {t}")
        print(t is str)
        if t is str:
            return SearchFieldDataType.String
        # fallback to string
        logger.warning(f"Falling back to string type for value: {value} of type {t}")
        return SearchFieldDataType.String
        
    def _build_fields(self, sample: Dict[str, Any], key_field: str):
        AzureKeyCredential, SearchClient, SearchIndexClient, AzureOpenAI, SearchIndex, SearchField, SearchFieldDataType, SimpleField, SearchableField, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration, SemanticSearch, SemanticField, SemanticConfiguration, SemanticPrioritizedFields = self._ensure_sdk()

        fields = []
        # Add key field
        if key_field not in sample:
            fields.append(SimpleField(name=key_field, type=SearchFieldDataType.String, key=True))
        else:
            fields.append(SimpleField(name=key_field, type=SearchFieldDataType.String, key=True))

        # Add regular fields
        for k, v in sample.items():
            logger.info(f"================={k}============")
            if k == key_field:
                continue
            logger.info(f"#### Infer field type for field: {k}")
            typ = self._infer_field_type(v)
            logger.info(f"#### Inferred type for field {k}: {typ}")
            if typ == SearchFieldDataType.String:
                fields.append(SearchableField(name=k, type=SearchFieldDataType.String))
            else:
                fields.append(SimpleField(name=k, type=typ))

        # Add vector field if vectorization is enabled
        if self.config.get("vectorization"):
            vector_field = self.config.get("vector_field", "contentVector")
            _, dimensions = self._build_vector_search_config()
            fields.append(
                SearchField(
                    name=vector_field,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=dimensions,
                    vector_search_profile_name="vector-profile-1"
                )
            )

        return fields

    def create_index(self, sample: Dict[str, Any]) -> bool:
        try:
            AzureKeyCredential, SearchClient, SearchIndexClient, AzureOpenAI, SearchIndex, SearchField, SearchFieldDataType, SimpleField, SearchableField, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration, SemanticSearch, SemanticField, SemanticConfiguration, SemanticPrioritizedFields = self._ensure_sdk()

            endpoint = self.config["aisearch_endpoint"]
            api_key = self.config["aisearch_api_key"]
            index_name = self.config["aisearch_index_name"]
            key_field = self.config.get("key_field", "id")

            index_client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
            fields = self._build_fields(sample, key_field)

            # Prepare semantic settings if configured
            semantic_settings = self._build_semantic_settings()

            # Create index with vector search if enabled
            if self.config.get("vectorization"):
                vector_search, _ = self._build_vector_search_config()
                if semantic_settings is not None:
                    index = SearchIndex(
                        name=index_name,
                        fields=fields,
                        vector_search=vector_search,
                        semantic_search=semantic_settings
                    )
                else:
                    index = SearchIndex(
                        name=index_name,
                        fields=fields,
                        vector_search=vector_search
                    )
            else:
                if semantic_settings is not None:
                    index = SearchIndex(name=index_name, fields=fields, semantic_settings=semantic_settings)
                else:
                    index = SearchIndex(name=index_name, fields=fields)

            index_client.create_or_update_index(index)
            logger.info(f"Azure Search index '{index_name}' created/updated with vectorization={self.config.get('vectorization', False)} semantic={semantic_settings is not None}")
            return True
        except Exception as ex:
            logger.exception("AzureSearchIndexer.create_index failed")
            return False

    def upload_documents(self, docs: List[Dict[str, Any]]) -> bool:
        try:
            AzureKeyCredential, SearchClient, SearchIndexClient, AzureOpenAI, SearchIndex, SearchField, SearchFieldDataType, SimpleField, SearchableField, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration, SemanticSearch, SemanticField, SemanticConfiguration, SemanticPrioritizedFields = self._ensure_sdk()
            endpoint = self.config["aisearch_endpoint"]
            api_key = self.config["aisearch_api_key"]
            index_name = self.config["aisearch_index_name"]
            key_field = self.config.get("key_field", "id")
            
            # Add IDs if missing
            from uuid import uuid4
            for d in docs:
                if key_field not in d:
                    d[key_field] = str(uuid4())
                elif not isinstance(d[key_field], str):
                    d[key_field] = str(d[key_field])

            # Add vector embeddings if enabled
            if self.config.get("vectorization"):
                vector_field = self.config.get("vector_field", "contentVector")
                content_field = self.config.get("content_field", "content")
                
                for doc in docs:
                    if content_field in doc:
                        try:
                            embedding = self._get_embeddings(str(doc[content_field]))
                            doc[vector_field] = embedding
                        except Exception as e:
                            logger.error(f"Failed to get embedding for document {doc.get(key_field)}: {str(e)}")
                            continue

            client = SearchClient(endpoint=endpoint, index_name=index_name, 
                               credential=AzureKeyCredential(api_key))
            
            logger.info(f"Uploading {len(docs)} documents to index {index_name}")
            result = client.upload_documents(documents=docs)
            
            failed = [r for r in result if not r.succeeded]
            if failed:
                logger.error(f"Some documents failed to upload: {failed}")
                return False
                
            logger.info("Documents uploaded successfully")
            return True
            
        except Exception:
            logger.exception("AzureSearchIndexer.upload_documents failed")
            return False

    def index(self, rows: List[Dict[str, Any]]) -> bool:
        """High level: create index (based on first row) and upload all rows."""
        if not rows:
            logger.error("AzureSearchIndexer.index called with empty rows")
            return False
            
        try:
            if not self.validate_config():
                return False
                
            sample = rows[0]
            logger.info(f"Creating/updating index with sample: {sample}")
            
            ok = self.create_index(sample)
            if not ok:
                return False
                
            ok2 = self.upload_documents(rows)
            return ok2
            
        except Exception:
            logger.exception("AzureSearchIndexer.index failed")
            return False