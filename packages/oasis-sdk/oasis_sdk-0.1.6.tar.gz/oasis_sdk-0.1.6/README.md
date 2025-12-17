# OASIS-SDK

## 1. Concept

OASIS-LLM-PROXY-CLIENT는 **다양한 LLM Provider를 통합된 단일 클라이언트**로 제공하는 Python 라이브러리입니다. 공식 SDK 및 LangChain을 얇게 wrapping하여 사내 규칙에 맞는 필드 입력과 프록시 서버를 통한 키 주입을 지원합니다.

**지원하는 LLM Provider:**

- 🟢 **OpenAI**: GPT-4o, GPT-4, GPT-3.5, Embedding 모델
- 🔵 **Azure OpenAI**: Azure 배포된 OpenAI 모델들
- 🟠 **Google**: Gemini 2.0 Pro 등
- ⚫ **XAI**: Grok 모델
- 🟣 **Anthropic**: Claude Sonnet 시리즈
- 🎯 **Oasis**: 자체 LLM 모델 및 임베딩

**주요 특징:**

- 🔄 **통합 클라이언트**: 하나의 `Oasis` 클라이언트로 모든 LLM Provider 사용
- 🎯 **자동 프로바이더 선택**: 모델 ID만으로 적절한 프로바이더 자동 선택
- 🔗 **완전한 호환성**: 원본 라이브러리의 모든 기능을 그대로 사용 가능
- 🛡️ **통합 인증**: 프록시 서버를 통한 안전한 키 관리
- 🧪 **Provider별 테스트**: 각 Provider별로 독립적인 테스트 지원

## 2. Usage

### 2.1 설치

```bash
pip install oasis-sdk
```

### 2.2 환경 설정

프록시 서버 URL을 환경변수로 설정할 수 있습니다

- 기본값은 이미 설정되어있음

```bash
export OASIS_PROXY_URL="https://your-proxy-server.com"
```

또는 클라이언트 생성시 직접 지정:

```python
client = Oasis(
    proxy_url="https://your-proxy-server.com",
    # ... 기타 매개변수
)
```

### 2.3 사용 예시

**client parameters**

[required]

- account_id: 계정 ID
- user_uuid: 사용자 UUID
- workspace_uuid: 워크스페이스 UUID
- tenant_uuid: 테넌트 UUID
- plugin_name: 호출한 시스템 명 (ex: chatbot, mcp1, rag-mcp 등)

[optional]

- proxy_url: LLM 프록시 서버 URL (환경변수 `OASIS_PROXY_URL`에서 자동 로드)
- user_ip: 사용자 IP (기본값: 127.0.0.1)

[auto]

- root_id: 클라이언트 생성시 발급
- req_id: 요청시마다 발급

📍 **주의**

- 1번의 연속적인 수행에서 root_id는 고정되어야 함
- 연계되는 시스템에서는 클라이언트 생성시 초기 발급된 root_id를 주입하여 사용

#### 2.3.1 SDK (통합된 OpenAI 클라이언트)

**통합된 다중 Provider SDK 래퍼**

> 📍 **중요**: 모든 LLM Provider(OpenAI, Azure, Google, XAI, Anthropic, Oasis)가 동일한 `Oasis` 클라이언트를 사용합니다. 모델 ID만으로 자동으로 적절한 프로바이더를 선택합니다.

```python
import oasis
# 또는
from oasis.compatible.sdk import Oasis, AsyncOasis

# 동기 클라이언트
with Oasis(
    account_id="your_account_id",
    user_uuid="your_uuid",
    workspace_uuid="your_workspace_uuid",
    tenant_uuid="your_tenant_uuid",
    plugin_name="your_system"
) as client:
    print(f"Client base URL: {client.base_url}")

    # OpenAI 모델 사용 예시
    openai_resp = client.chat.completions.create(
        model="your_openai_model_uuid",  # OpenAI 모델 UUID
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
    )
    print("OpenAI Response:", openai_resp.choices[0].message.content)

    # Google Gemini 모델 사용 예시
    google_resp = client.chat.completions.create(
        model="your_google_model_uuid",  # Google Gemini UUID
        messages=[
            {"role": "user", "content": "Hello from Google Gemini!"}
        ],
    )
    print("Google Response:", google_resp.choices[0].message.content)

    # Anthropic Claude 모델 사용 예시
    anthropic_resp = client.chat.completions.create(
        model="your_anthropic_model_uuid",  # Claude 모델 UUID
        messages=[
            {"role": "user", "content": "Hello from Claude!"}
        ],
    )
    print("Anthropic Response:", anthropic_resp.choices[0].message.content)

    # Azure OpenAI 모델 사용 예시 (동일한 클라이언트로!)
    azure_resp = client.chat.completions.create(
        model="your_azure_model_uuid",  # Azure deployment UUID
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello from Azure!"}
        ],
        max_tokens=100,  # Azure 모델 사용시 토큰 제한
    )
    print("Azure Response:", azure_resp.choices[0].message.content)

    # 스트리밍 (OpenAI 모델)
    stream = client.chat.completions.create(
        model="your_openai_model_uuid",
        messages=[{"role": "user", "content": "Tell me a short story"}],
        stream=True,
    )
    print("OpenAI Stream:")
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")

    # 스트리밍 (Azure 모델)
    azure_stream = client.chat.completions.create(
        model="your_azure_model_uuid",
        messages=[{"role": "user", "content": "Count to 3"}],
        max_tokens=50,
        stream=True,
    )
    print("Azure Stream:")
    for chunk in azure_stream:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")

    # 임베딩 (동일한 모델 ID가 OpenAI/Azure 모두 지원)
    embedding_resp = client.embeddings.create(
        model="your_embedding_uuid",  # 임베딩 모델 UUID
        input=["This sentence will be embedded.", "Another test sentence."],
    )
    print(f"Embedding vector dimension: {len(embedding_resp.data[0].embedding)}")

    # Rerank 사용 예시
    rerank_resp = client.rerank(
        model="your_rerank_model_uuid",  # Rerank 모델 UUID
        query="Python programming",
        documents=[
            "Python is a high-level programming language.",
            "JavaScript is used for web development.",
            "Python is popular for data science and machine learning.",
        ],
        top_n=2,  # 상위 2개 결과 반환
    )
    print(f"Rerank results: {rerank_resp['results']}")

# 비동기 클라이언트 (동일한 방식으로 OpenAI/Azure 모두 지원)
import asyncio

async def async_example():
    async with AsyncOasis(
        account_id="your_account_id",
        user_uuid="your_uuid",
        workspace_uuid="your_workspace_uuid",
        tenant_uuid="your_tenant_uuid",
        plugin_name="your_system"
    ) as client:
        # 비동기 채팅 완성 (OpenAI)
        openai_resp = await client.chat.completions.create(
            model="model_uuid",
            messages=[{"role": "user", "content": "Hello OpenAI!"}],
        )
        print("Async OpenAI:", openai_resp.choices[0].message.content)

        # 비동기 채팅 완성 (Azure)
        azure_resp = await client.chat.completions.create(
            model="model_uuid",
            messages=[{"role": "user", "content": "Hello Azure!"}],
            max_tokens=50,
        )
        print("Async Azure:", azure_resp.choices[0].message.content)

        # 비동기 스트리밍
        stream = await client.chat.completions.create(
            model="model_uuid",
            messages=[{"role": "user", "content": "Count to 5"}],
            stream=True,
        )
        print("Async Stream:")
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n")

        # 비동기 임베딩
        embedding_resp = await client.embeddings.create(
            model="your_model_uuid",
            input=["Async embedding test"],
        )
        print(f"Async embedding vector: {embedding_resp.data[0].embedding[:5]}...")

        # 비동기 Rerank
        rerank_resp = await client.rerank(
            model="your_rerank_model_uuid",
            query="Machine learning",
            documents=[
                "Machine learning is a subset of artificial intelligence.",
                "Deep learning uses neural networks.",
                "Python is a versatile programming language.",
            ],
            top_n=2,
        )
        print(f"Async rerank results: {rerank_resp['results']}")

# 비동기 함수 실행
asyncio.run(async_example())
```

#### 2.3.2 LangChain (통합된 OpenAI 래퍼)

> 📍 **중요**: LangChain도 통합된 `ChatOasis`와 `OasisEmbedding`을 사용합니다. 모델 ID로 모든 Provider를 자동 구분합니다.

```python
from oasis.compatible.langchain import ChatOasis, OasisEmbedding

# OpenAI 모델을 사용하는 채팅 예시
openai_llm = ChatOasis(
    account_id="your_account_id",
    user_uuid="your_uuid",
    workspace_uuid="your_workspace_uuid",
    tenant_uuid="your_tenant_uuid",
    model_name="model_uuid",  # OpenAI 모델 UUID
    plugin_name="langchain_openai_test"
)

# Azure 모델을 사용하는 채팅 예시 (동일한 클래스!)
azure_llm = ChatOasis(
    account_id="your_account_id",
    user_uuid="your_uuid",
    workspace_uuid="your_workspace_uuid",
    tenant_uuid="your_tenant_uuid",
    model_name="model_uuid",  # Azure deployment UUID
    plugin_name="langchain_azure_test"
)

try:
    # OpenAI 모델 호출
    openai_resp = openai_llm.invoke("Hello from OpenAI via LangChain!")
    print("OpenAI Response:", openai_resp.content)

    # Azure 모델 호출 (동일한 인터페이스!)
    azure_resp = azure_llm.invoke("Hello from Azure via LangChain!")
    print("Azure Response:", azure_resp.content)

    # OpenAI 스트리밍
    print("OpenAI Stream:")
    for chunk in openai_llm.stream("Tell me a short story"):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n")

    # Azure 스트리밍
    print("Azure Stream:")
    for chunk in azure_llm.stream("Count to 3"):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n")

    # 비동기 호출 예시
    async def async_langchain_example():
        # 비동기 OpenAI 호출
        openai_async_resp = await openai_llm.ainvoke("Async OpenAI LangChain!")
        print("Async OpenAI:", openai_async_resp.content)

        # 비동기 Azure 호출
        azure_async_resp = await azure_llm.ainvoke("Async Azure LangChain!")
        print("Async Azure:", azure_async_resp.content)

        # 비동기 스트리밍
        print("Async OpenAI Stream:")
        async for chunk in openai_llm.astream("Async streaming test"):
            if chunk.content:
                print(chunk.content, end="", flush=True)
        print("\n")

        # Rerank 비동기 호출
        rerank_resp = await openai_llm.arerank(
            model="your_rerank_model_uuid",
            query="Python data science",
            documents=[
                "Python is widely used in data science.",
                "R is another popular language for statistics.",
                "Python has excellent machine learning libraries.",
            ],
            top_n=2,
        )
        print(f"Async rerank results: {rerank_resp['results']}")

    # 비동기 함수 실행
    import asyncio
    asyncio.run(async_langchain_example())

finally:
    # 리소스 정리
    openai_llm.close()
    azure_llm.close()

# 임베딩 예시 (OpenAI/Azure 모두 동일한 클래스 사용)
openai_embedding = OasisEmbedding(
    account_id="your_account_id",
    user_uuid="your_uuid",
    workspace_uuid="your_workspace_uuid",
    tenant_uuid="your_tenant_uuid",
    model_name="model_uuid",  # 임베딩 모델 UUID (OpenAI/Azure 공통)
    plugin_name="langchain_embedding_test"
)

try:
    # 동기 임베딩 (여러 문서)
    vectors = openai_embedding.embed_documents([
        "First document for embedding",
        "Second document for embedding",
        "Third document with different content"
    ])
    print(f"Embedded {len(vectors)} documents, vector dimension: {len(vectors[0])}")

    # 동기 임베딩 (단일 쿼리)
    query_vector = openai_embedding.embed_query("What was the main topic?")
    print(f"Query vector dimension: {len(query_vector)}")

    # 비동기 임베딩
    async def async_embedding_example():
        async_vectors = await openai_embedding.aembed_documents([
            "Async embedding test document"
        ])
        print(f"Async embedded vector dimension: {len(async_vectors[0])}")

    asyncio.run(async_embedding_example())

finally:
    # 리소스 정리
    await openai_embedding.aclose()

# Rerank 예시 (ChatOasis 또는 OasisEmbedding 모두 사용 가능)
oasis_chat = ChatOasis(
    account_id="your_account_id",
    user_uuid="your_uuid",
    workspace_uuid="your_workspace_uuid",
    tenant_uuid="your_tenant_uuid",
    model_name="your_rerank_model_uuid",
    plugin_name="rerank_test"
)

try:
    # 동기 Rerank
    rerank_result = oasis_chat.rerank(
        model="your_rerank_model_uuid",
        query="Best practices for Python programming",
        documents=[
            "Python uses indentation for code blocks.",
            "Python is known for its readability.",
            "JavaScript uses curly braces for code blocks.",
            "Python has a large standard library.",
        ],
        top_n=3,
    )
    print(f"Top {len(rerank_result['results'])} reranked documents:")
    for idx, result in enumerate(rerank_result['results'], 1):
        print(f"{idx}. Score: {result.get('relevance_score', 'N/A')} - {result.get('document', 'N/A')}")

    # 비동기 Rerank
    async def async_rerank_example():
        async_result = await oasis_chat.arerank(
            model="your_rerank_model_uuid",
            query="Machine learning with Python",
            documents=[
                "Python has powerful ML libraries like scikit-learn.",
                "Java is used in enterprise applications.",
                "TensorFlow and PyTorch are popular Python ML frameworks.",
            ],
            top_n=2,
        )
        print(f"Async rerank results: {async_result['results']}")

    asyncio.run(async_rerank_example())

finally:
    oasis_chat.close()
```

## 3. 모범 사례

### 3.1 리소스 관리

**권장: Context Manager 사용**

```python
# 동기 클라이언트
with Oasis(...) as client:
    # 작업 수행
    resp = client.chat.completions.create(...)

# 비동기 클라이언트
async with AsyncOasis(...) as client:
    # 작업 수행
    resp = await client.chat.completions.create(...)
```

**수동 리소스 관리**

```python
# 동기
client = Oasis(...)
try:
    # 작업 수행
    resp = client.chat.completions.create(...)
finally:
    client.close()

# 비동기
client = AsyncOasis(...)
try:
    # 작업 수행
    resp = await client.chat.completions.create(...)
finally:
    await client.aclose()
```

### 3.2 스트리밍 처리

```python
# 동기 스트리밍
with Oasis(...) as client:
    stream = client.chat.completions.create(
        model="model_id",
        messages=[...],
        stream=True
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

# 비동기 스트리밍
async with AsyncOasis(...) as client:
    stream = await client.chat.completions.create(
        model="model_id",
        messages=[...],
        stream=True
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
```

### 3.3 에러 핸들링

```python
from oasis.sdk.openai import Oasis
from openai import OpenAIError

with Oasis(...) as client:
    try:
        resp = client.chat.completions.create(
            model="model_id",
            messages=[{"role": "user", "content": "Hello"}]
        )
    except OpenAIError as e:
        print(f"OpenAI API 에러: {e}")
    except Exception as e:
        print(f"기타 에러: {e}")
```

## 4. 의존성

- Python 3.11.x
- openai 1.97.0
- langchain-openai 0.3.28

## 6. 개발자 가이드

### 6.1 새로운 Provider 추가

새로운 LLM Provider를 추가하려면:

1. **환경변수 설정**: `tests/test_env.py`에 새 Provider의 모델 UUID 추가
2. **테스트 파일 생성**:
   - `tests/test_oasis_{provider}.py` (SDK 래퍼용)
   - `tests/test_oasis_lc_{provider}.py` (LangChain 래퍼용)
3. **Provider 식별**: 환경변수 prefix로 Provider 구분 (예: `NEWPROVIDER_`)

### 6.2 코드 기여

1. **브랜치 생성**: `git checkout -b feature/new-feature`
2. **테스트 작성**: Provider별 테스트 파일에 새 기능 테스트 추가
3. **문서 업데이트**: README.md에 새 기능 설명 추가
4. **Pull Request**: 변경사항을 설명하는 PR 생성

## 7. 라이선스

이 프로젝트는 [LICENSE](LICENSE) 파일에 명시된 라이선스를 따릅니다.

## 8. 문의 및 지원

- **이슈 리포트**: GitHub Issues를 통해 버그나 기능 요청 제출
- **기술 문의**: 개발팀에게 직접 연락
- **기여 가이드**: CONTRIBUTING.md 참조 (있는 경우)

## 5. 테스트

### 5.1 전체 테스트 실행

```bash
# 모든 테스트 실행
python -m pytest tests/
```

### 5.2 Provider별 테스트

**SDK 래퍼 테스트 (Oasis 클라이언트)**

```bash
# OpenAI Provider
python -m pytest tests/test_oasis_openai.py

# Azure OpenAI Provider
python -m pytest tests/test_oasis_azure.py

# Google Provider
python -m pytest tests/test_oasis_google.py

# XAI Provider
python -m pytest tests/test_oasis_xai.py

# Anthropic Provider
python -m pytest tests/test_oasis_anthropic.py

# Oasis Provider (자체 모델)
python -m pytest tests/test_oasis.py
```

**LangChain 래퍼 테스트**

```bash
# LangChain OpenAI Provider
python -m pytest tests/test_oasis_lc_openai.py

# LangChain Azure Provider
python -m pytest tests/test_oasis_lc_azure.py

# LangChain Google Provider
python -m pytest tests/test_oasis_lc_google.py

# LangChain XAI Provider
python -m pytest tests/test_oasis_lc_xai.py

# LangChain Anthropic Provider
python -m pytest tests/test_oasis_lc_anthropic.py

# LangChain Oasis Provider
python -m pytest tests/test_oasis_lc.py
```

### 5.3 특정 Provider 그룹 테스트

```bash
# OpenAI 관련 모든 테스트
python -m pytest tests/test_oasis_openai.py tests/test_oasis_lc_openai.py

# Azure 관련 모든 테스트
python -m pytest tests/test_oasis_azure.py tests/test_oasis_lc_azure.py

# 특정 패턴으로 테스트 실행
python -m pytest tests/test_*openai*.py  # OpenAI 관련
python -m pytest tests/test_*azure*.py   # Azure 관련
python -m pytest tests/test_*lc*.py      # LangChain 관련
```

### 5.4 Provider별 분리의 장점

- **독립성**: 각 Provider의 문제가 다른 Provider에 영향을 주지 않음
- **선택적 테스트**: 필요한 Provider만 테스트하여 시간 단축
- **디버깅 용이성**: 특정 Provider에서 발생하는 문제를 빠르게 찾을 수 있음
- **CI/CD 최적화**: Provider별로 병렬 테스트 실행 가능

### 5.5 노트북 예시

실제 사용 예시는 `tests/notebooks/` 디렉토리의 Jupyter 노트북을 참고하세요:

- `openai.ipynb`: SDK 래퍼를 사용한 OpenAI 모델 예시
- `azure.ipynb`: SDK 래퍼를 사용한 Azure OpenAI 모델 예시
- `api.ipynb`: 다양한 Provider API 레벨 사용 예시

### 5.6 환경 변수 설정

테스트를 실행하기 전에 `tests/test_env.py`에서 필요한 모델 UUID와 인증 정보를 설정하세요:

```python
# tests/test_env.py
def set_env():
    os.environ["PROXY_URL"] = "http://your-proxy-server:port/api/proxy"
    os.environ["ACCOUNT_ID"] = "your_account_id"
    os.environ["USER_UUID"] = "your_user_uuid"
    os.environ["WORKSPACE_UUID"] = "your_workspace_uuid"
    os.environ["TENANT_UUID"] = "your_tenant_uuid"

    # Provider별 모델 UUID 설정
    os.environ["OPENAI_GPT_4O"] = "openai_model_uuid"
    os.environ["AOAI_OASIS_GPT_4_1"] = "azure_model_uuid"
    os.environ["GOOGLE_GEMINI_2_5_PRO"] = "google_model_uuid"
    # ... 기타 Provider UUID
```
