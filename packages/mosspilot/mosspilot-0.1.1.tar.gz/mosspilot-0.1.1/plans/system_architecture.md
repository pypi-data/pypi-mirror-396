# Moss 自动化测试框架系统架构

## 系统架构图

```mermaid
graph TB
    subgraph "测试执行层"
        A[pytest 执行引擎] --> B[测试用例调度器]
        B --> C[API测试模块]
        B --> D[UI测试模块] 
        B --> E[性能测试模块]
    end
    
    subgraph "核心框架层"
        F[配置管理器] --> G[数据库连接池]
        F --> H[日志管理器]
        F --> I[报告生成器]
        F --> J[监控代理]
    end
    
    subgraph "测试模块层"
        C --> K[httpx HTTP客户端]
        D --> L[playwright 浏览器驱动]
        E --> M[locust 性能引擎]
    end
    
    subgraph "数据存储层"
        N[测试数据库] --> O[用例数据表]
        N --> P[执行结果表]
        N --> Q[配置参数表]
    end
    
    subgraph "报告监控层"
        R[HTML报告模板] --> S[自定义报告生成]
        T[实时监控面板] --> U[企业监控系统集成]
    end
    
    subgraph "CI/CD集成层"
        V[Jenkins插件接口] --> W[测试结果回调]
        X[命令行接口] --> Y[批量执行脚本]
    end
    
    A --> F
    G --> N
    I --> R
    J --> T
    V --> A
    X --> A