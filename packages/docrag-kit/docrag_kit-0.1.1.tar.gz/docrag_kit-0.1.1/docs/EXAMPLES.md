# DocRAG Kit Examples

This document provides detailed examples of using DocRAG Kit with different project types.

## Table of Contents

- [Symfony Project Example](#symfony-project-example)
- [iOS Project Example](#ios-project-example)
- [General Documentation Project](#general-documentation-project)
- [Example Questions](#example-questions)
- [Configuration Examples](#configuration-examples)

## Symfony Project Example

### Setup

```bash
cd my-symfony-project
docrag init
```

**Interactive wizard responses:**
```
? Select LLM provider: OpenAI
? Enter OpenAI API key: sk-...
? Directories to index: docs/, src/, config/
? File extensions: .md, .txt, .php, .yaml, .twig
? Exclude patterns: vendor/, var/, node_modules/
? Project type: Symfony
? GitHub token (optional): [skip]
```

### Index Documentation

```bash
docrag index
```

**Output:**
```
📚 Indexing documents...
✓ Found 45 files to index
✓ Processing documents...
✓ Creating embeddings...
✓ Storing in vector database...

Statistics:
- Files processed: 45
- Chunks created: 234
- Total characters: 89,432

✅ Indexing complete!
```

### Example Questions

**Question 1: Architecture**
```
Q: "Какая архитектура используется в проекте?"
A: "Проект использует стандартную архитектуру Symfony с разделением на слои:
   - Controller layer для обработки HTTP запросов
   - Service layer для бизнес-логики
   - Repository layer для работы с базой данных
   - Entity layer для моделей данных"
```

**Question 2: Configuration**
```
Q: "Как настроить подключение к базе данных?"
A: "Для настройки подключения к базе данных отредактируйте файл .env:
   DATABASE_URL='mysql://user:password@127.0.0.1:3306/dbname'
   
   Затем выполните миграции:
   php bin/console doctrine:migrations:migrate"
```

**Question 3: API Endpoints**
```
Q: "Какие API endpoints доступны?"
A: "В проекте доступны следующие API endpoints:
   - GET /api/users - список пользователей
   - POST /api/users - создание пользователя
   - GET /api/users/{id} - получение пользователя
   - PUT /api/users/{id} - обновление пользователя
   - DELETE /api/users/{id} - удаление пользователя"
```

## iOS Project Example

### Setup

```bash
cd MyiOSApp
docrag init
```

**Interactive wizard responses:**
```
? Select LLM provider: Gemini
? Enter Gemini API key: AIza...
? Directories to index: docs/, Sources/, README.md
? File extensions: .md, .txt, .swift
? Exclude patterns: .build/, DerivedData/, Pods/
? Project type: iOS
? GitHub token (optional): [skip]
```

### Index Documentation

```bash
docrag index
```

### Example Questions

**Question 1: Architecture**
```
Q: "What architecture pattern is used in this app?"
A: "The app uses MVVM (Model-View-ViewModel) architecture with:
   - Models: Data structures and business logic
   - Views: SwiftUI views for UI
   - ViewModels: State management and data transformation
   - Services: Network and data persistence layers"
```

**Question 2: Navigation**
```
Q: "How is navigation implemented?"
A: "Navigation is implemented using SwiftUI's NavigationStack:
   - Root view: ContentView with NavigationStack
   - Navigation paths defined in NavigationCoordinator
   - Deep linking supported via URL schemes
   - State restoration handled automatically"
```

**Question 3: Data Persistence**
```
Q: "How is data persisted?"
A: "Data persistence uses Core Data with:
   - DataController managing the Core Data stack
   - Entity models defined in .xcdatamodeld
   - Repository pattern for data access
   - Background context for heavy operations"
```

## General Documentation Project

### Setup

```bash
cd my-docs-project
docrag init
```

**Interactive wizard responses:**
```
? Select LLM provider: OpenAI
? Enter OpenAI API key: sk-...
? Directories to index: docs/, guides/, README.md
? File extensions: .md, .txt
? Exclude patterns: .git/, node_modules/
? Project type: General Documentation
? GitHub token (optional): [skip]
```

### Example Questions

**Question 1: Getting Started**
```
Q: "How do I get started with this project?"
A: "To get started:
   1. Clone the repository
   2. Install dependencies: npm install
   3. Copy .env.example to .env
   4. Configure environment variables
   5. Run: npm start"
```

**Question 2: Configuration**
```
Q: "What configuration options are available?"
A: "Available configuration options in config.yaml:
   - server.port: Server port (default: 3000)
   - database.url: Database connection string
   - logging.level: Log level (debug, info, warn, error)
   - cache.enabled: Enable caching (true/false)"
```

## Example Questions

### Technical Questions

```
Q: "Как работает аутентификация?"
A: "Аутентификация реализована через JWT токены..."

Q: "What dependencies are required?"
A: "Required dependencies include..."

Q: "Какие есть команды для разработки?"
A: "Доступные команды для разработки..."
```

### Architecture Questions

```
Q: "Опиши архитектуру проекта"
A: "Проект использует следующую архитектуру..."

Q: "How are components organized?"
A: "Components are organized in the following structure..."

Q: "Какие паттерны проектирования используются?"
A: "В проекте используются следующие паттерны..."
```

### Configuration Questions

```
Q: "Как настроить окружение для разработки?"
A: "Для настройки окружения выполните..."

Q: "What environment variables are needed?"
A: "Required environment variables..."

Q: "Где хранятся конфигурационные файлы?"
A: "Конфигурационные файлы находятся в..."
```

## Configuration Examples

### Minimal Configuration

```yaml
project:
  name: "my-project"
  type: "general"

llm:
  provider: "openai"
  embedding_model: "text-embedding-3-small"
  llm_model: "gpt-4o-mini"
  temperature: 0.3

indexing:
  directories:
    - "docs/"
  extensions:
    - ".md"
  exclude_patterns:
    - ".git/"

chunking:
  chunk_size: 1000
  chunk_overlap: 200

retrieval:
  top_k: 5
```

### Symfony Configuration

```yaml
project:
  name: "symfony-app"
  type: "symfony"

llm:
  provider: "openai"
  embedding_model: "text-embedding-3-small"
  llm_model: "gpt-4o-mini"
  temperature: 0.3

indexing:
  directories:
    - "docs/"
    - "src/"
    - "config/"
    - "templates/"
  extensions:
    - ".md"
    - ".txt"
    - ".php"
    - ".yaml"
    - ".twig"
  exclude_patterns:
    - "vendor/"
    - "var/"
    - "node_modules/"
    - ".git/"

chunking:
  chunk_size: 1500
  chunk_overlap: 300

retrieval:
  top_k: 7
```

### iOS Configuration

```yaml
project:
  name: "MyiOSApp"
  type: "ios"

llm:
  provider: "gemini"
  embedding_model: "models/embedding-001"
  llm_model: "gemini-1.5-flash"
  temperature: 0.3

indexing:
  directories:
    - "docs/"
    - "Sources/"
    - "README.md"
  extensions:
    - ".md"
    - ".txt"
    - ".swift"
  exclude_patterns:
    - ".build/"
    - "DerivedData/"
    - "Pods/"
    - ".git/"

chunking:
  chunk_size: 1200
  chunk_overlap: 250

retrieval:
  top_k: 6
```

### Custom Prompt Configuration

```yaml
project:
  name: "custom-project"
  type: "custom"

llm:
  provider: "openai"
  embedding_model: "text-embedding-3-small"
  llm_model: "gpt-4o-mini"
  temperature: 0.3

indexing:
  directories:
    - "docs/"
  extensions:
    - ".md"
  exclude_patterns:
    - ".git/"

chunking:
  chunk_size: 1000
  chunk_overlap: 200

retrieval:
  top_k: 5

prompt:
  template: |
    You are an expert in {project_type}.
    Use the following context to answer the question.
    
    Rules:
    - Answer precisely based on the provided context
    - If information is not in the context, say so honestly
    - Provide code examples when relevant
    - Support both Russian and English
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
```

## Tips and Best Practices

### Indexing

1. **Include relevant directories**: Only index documentation and code that users will ask about
2. **Exclude build artifacts**: Always exclude vendor/, node_modules/, build/, etc.
3. **Choose appropriate chunk size**: Larger chunks (1500+) for detailed docs, smaller (800-1000) for code
4. **Reindex after major changes**: Run `docrag reindex` after significant documentation updates

### Querying

1. **Be specific**: "How do I configure database?" is better than "database?"
2. **Use natural language**: Ask questions as you would to a colleague
3. **Include context**: "How do I deploy to production?" vs "How do I deploy?"
4. **Try both languages**: System works well with both Russian and English

### Configuration

1. **Adjust top_k**: Increase for complex questions, decrease for simple ones
2. **Tune chunk_overlap**: Higher overlap (300+) for better context continuity
3. **Choose right provider**: OpenAI for quality, Gemini for cost-effectiveness
4. **Use project templates**: They provide optimized prompts for specific domains

### Security

1. **Never commit .env**: Always keep API keys in gitignored .env file
2. **Use .env.example**: Provide template for team members
3. **Rotate keys regularly**: Change API keys periodically
4. **Monitor usage**: Check API usage to avoid unexpected costs
