# Lacrei Models

Pacote centralizado para os modelos de domínio (`models.py`) do ecossistema Lacrei.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 Objetivo

Centralizar todos os modelos do Django utilizados pelas aplicações Lacrei, permitindo:

- **Modularidade:** Desacoplar a camada de dados da lógica de aplicação.
- **Reuso:** Serviços diferentes podem consumir os mesmos modelos de forma consistente.
- **Governança e Consistência:** Ponto único de verdade para estrutura de dados.

É uma dependência interna, destinada a ser usada por aplicações como `lacrei-api`.

---

### Configurações Iniciais

1.  **Clone o Repositório, na mesmo local onde se encontra a lacrei-api e a lacrei-migrations:**
```bash
    git clone https://github.com/Lacrei/lacrei-models.git
    cd lacrei-models
```

2.  **Instale as Dependências:**
```bash
    make install
    poetry add lacrei-models
```
---

## ⚙️ Uso

Para testar localmente as mudanças na models antes de pubicar no PyPI:
```bash
poetry add --editable C:/local onde se encontra o lacrei-models
```

Importe os modelos no código:

```python
from lacrei_models.address.models import Address
from lacrei_models.client.models import User
from lacrei_models.appointments.models import Appointment
from lacrei_models.professional.models import Professional
from lacrei_models.notification.models import Notification
from lacrei_models.payment.models import Payment
from lacrei_models.sync.models import GoogleAccount
```

---



**Comandos principais:**

```bash
make test      # Rodar testes
make format    # Formatar código
make lint      # Verificar estilo e erros
make quality   # Rodar todas as verificações
```

---

## 🚀 Publicação no PyPI

Enviar atualizações para o github em uma nova branch e criar o PR
```bash
    git push origin branch
```
1- Ir até o actions dentro do repositório lacrei-models
2- Clicar em publish package
3- e depois ir em run workflow e selecionar a sua branch
4- A versão to publish deve ser uma versão acima da atual. Verificar no PyPI a ultima versão para evitar conflitos.
