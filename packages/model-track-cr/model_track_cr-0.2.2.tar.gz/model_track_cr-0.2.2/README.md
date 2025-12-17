# model-track-cr

O **model-track-cr** é uma biblioteca Python voltada para **binning, WOE, estabilidade e monitoramento de variáveis** em modelos de Machine Learning, com foco em **modelos de crédito e risco**.

O projeto foi construído seguindo rigorosamente **Test-Driven Development (TDD)**, garantindo:
- qualidade de código
- segurança para refatorações
- documentação viva através dos testes

---

## 📦 Estrutura do Projeto
```bash
.
├── Makefile
├── README.md
├── exemplo_uso.ipynb
├── poetry.lock
├── pyproject.toml
├── pytest.ini
├── src
│   └── model_track
│       ├── binning
│       ├── encoding
│       ├── stability
│       ├── stats
│       └── woe
├── tests
│   ├── conftest.py
│   ├── test_bin_applier.py
│   ├── test_tree_binning.py
│   ├── test_quantile_binning.py
│   ├── test_summary.py
│   └── test_woe.py
└── uv.lock
````

---

## 🧰 Ferramentas Utilizadas

- **Poetry** — gestão de dependências e versionamento
- **pytest** — testes automatizados
- **pytest-cov / coverage** — cobertura de código
- **Makefile** — automação de rotinas
- **GitHub Actions** — CI/CD
- **Git Flow** — fluxo de desenvolvimento e release

---
## 🚀 Instalação


Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/model-track-cr.git
cd model-track-cr
```
Instale as dependências:

```bash
poetry install
```
Ou via Makefile:
```bash
make install
```


🧪 Testes e Qualidade

Rodar testes:
```bash
make test
```
Rodar testes com cobertura:
```bash
make cov
```
O relatório HTML ficará disponível em:


`htmlcov/index.html`




🛠 Desenvolvimento (TDD)

1️⃣ Ativar ambiente virtual
```bash
poetry shell
````

2️⃣ Fluxo TDD recomendado

1. Criar ou atualizar um teste em tests/
2. Rodar:
```bash
make test
```

3.	Implementar o código mínimo para passar
4.	Refatorar com segurança
5.	Validar cobertura:
```bash
make cov
```




🧩 Fixtures Globais

Fixtures compartilhadas devem ficar em:

`tests/conftest.py`

O `pytest` carrega esse arquivo automaticamente.

---
## 🤝 Como Contribuir (Git Flow)

🔹 Regras Importantes
*	❌ Não é permitido push direto na main
*	✅ Toda mudança passa por Pull Request
*	✅ CI deve estar verde
*	✅ Testes obrigatórios
*	✅ TDD é mandatório



1️⃣ Criar branch a partir da main

```bash
git checkout main
git pull origin main
git checkout -b feature/nome-da-feature
```
Ou para correções:
```bash
git checkout -b fix/nome-do-fix
```

2️⃣ Desenvolver seguindo TDD

```bash
make test
make cov
```


3️⃣ Commitar mudanças

```bash
git add .
git commit -m "feat: descrição clara da mudança"
```



4️⃣ Push da branch
```bash
git push origin feature/nome-da-feature
```

5️⃣ Abrir Pull Request

O PR deve conter:
*	descrição clara
*	motivação
*	exemplos de uso (se aplicável)

O PR só será aceito se:
*	CI passar
*	cobertura mínima for respeitada
*	arquitetura estiver consistente

---
🚢 Processo de Release e Publicação (Git Flow + Poetry)
____
🔖 Versionamento Semântico

Usamos Poetry para versionamento:
*	patch → correções (0.1.0 → 0.1.1)
*	minor → novas funcionalidades (0.1.0 → 0.2.0)
*	major → breaking changes (1.0.0 → 2.0.0)



1️⃣ Criar branch de release

```bash
git checkout main
git pull origin main
git checkout -b release/patch
```



2️⃣ Atualizar versão automaticamente
```bash
poetry version patch
```
Exemplo:

Bumping version from `0.1.0` to `0.1.1`




3️⃣ Commit da versão
```bash
git add pyproject.toml
git commit -m "Bump version to 0.1.1"
```



4️⃣ Push da branch de release
```bash
git push origin release/patch
```



5️⃣ Abrir Pull Request → main
*	Base: `main`
*	Compare: `release/patch`

A CI será executada automaticamente.



6️⃣ Merge do PR

Após aprovação e CI verde.



7️⃣ Criar tag e publicar
```bash
git checkout main
git pull origin main

git tag v0.1.1
git push origin v0.1.1
```
👉 A GitHub Action de publish será disparada automaticamente
👉 O pacote será publicado no PyPI



📚 Roadmap (em evolução)
*	Estabilidade de WOE por safra
*	PSI automático
*	Seleção de variáveis por estabilidade
*	CLI para análises rápidas
*	Integração com pipelines de crédito
*	Relatórios automáticos


📝 Licença

MIT
