<div align="center">

```
██████╗  ██████╗ ██████╗ ████████╗    ███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗
██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
██████╔╝██║   ██║██████╔╝   ██║       ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
██╔═══╝ ██║   ██║██╔══██╗   ██║       ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
██║     ╚██████╔╝██║  ██║   ██║       ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
```

**Ferramenta de varredura de rede assíncrona com TUI brutalista — feita em Python puro.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Liragbr/PortScanner?style=flat-square)](https://github.com/Liragbr/PortScanner/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?style=flat-square)]()

</div>

---

## Sobre

**Port Scanner** é uma ferramenta de linha de comando para varredura de portas TCP/IP, desenvolvida inteiramente em Python. Combina um motor de varredura assíncrono (via `asyncio`) com uma interface de terminal (TUI) interativa e esteticamente agressiva, construída com a biblioteca `Rich`.

O projeto foi criado com foco em **performance**, **usabilidade** e **aprendizado prático de redes e segurança ofensiva**.

---

## Funcionalidades

| Recurso | Descrição |
|---|---|
|  **Motor Assíncrono** | Varredura ultrarrápida via `asyncio`, escaneando múltiplas portas em paralelo |
|  **Modo Stealth (SYN)** | Half-open SYN scan via `Scapy` — maior evasão, requer privilégios de administrador |
|  **TUI Brutalista** | Dashboard interativo com painéis, animações e feedback em tempo real via `Rich` |
|  **Export JSON** | Geração de relatórios estruturados em `.json` prontos para ingestão em SIEMs |
|  **Sanitização de Alvo** | Limpa e valida URLs completas automaticamente (remove `http://`, paths, etc.) |
| 📦 **Executável Standalone** | Release `.exe` sem dependência de Python instalado na máquina |

---

## Estrutura do Projeto

```
PortScanner/
├── portscanner/          # Pacote principal
│   └── cli.py            # Interface CLI / TUI (entry point lógico)
├── run.py                # Ponto de entrada da aplicação
├── requirements.txt      # Dependências do projeto
└── .gitignore
```

---

## Como Usar

### Opção 1 — Executável (Windows, sem Python)

1. Acesse a página de [**Releases**](https://github.com/Liragbr/PortScanner/releases)
2. Baixe o arquivo `PortScanner.exe`
3. Execute com duplo clique ou via terminal:

```cmd
PortScanner.exe
```

### Opção 2 — Executar via Python

**Pré-requisitos:** Python 3.10+

```bash
# Clone o repositório
git clone https://github.com/Liragbr/PortScanner.git
cd PortScanner

# Instale as dependências
pip install -r requirements.txt

# Execute
python run.py
```

> ⚠️ Para usar o **Modo Stealth (SYN Scan)**, execute como administrador/root.

---

## Dependências

| Biblioteca | Versão | Finalidade |
|---|---|---|
| `rich` | 15.0.0 | Interface TUI, painéis, animações e output colorido |
| `scapy` | 2.7.0 | Construção de pacotes de rede para SYN scan (modo stealth) |
| `tqdm` | 4.67.3 | Barras de progresso durante a varredura |

---

## Modos de Varredura

### TCP Connect Scan (padrão)
Realiza o handshake TCP completo. Não requer privilégios especiais. Detectável por firewalls e IDS.

### SYN Stealth Scan (modo admin)
Envia apenas o pacote SYN e analisa a resposta sem completar o handshake (half-open). Muito mais furtivo e rápido. Utiliza `Scapy` para construção manual dos pacotes.

---

## Saída de Relatório (JSON)

```json
{
  "target": "192.168.1.1",
  "scan_date": "2026-05-16T21:10:00",
  "open_ports": [
    { "port": 22, "service": "SSH", "state": "open" },
    { "port": 80, "service": "HTTP", "state": "open" },
    { "port": 443, "service": "HTTPS", "state": "open" }
  ],
  "total_scanned": 1000,
  "total_open": 3
}
```

---

## Roadmap

- [ ] Detecção de serviço via banner grabbing
- [ ] Suporte a varredura de sub-redes (CIDR)
- [ ] UDP scan
- [ ] Output em formato CSV e HTML
- [ ] Integração com geolocalização de IPs
- [ ] Suporte nativo a Linux e macOS no executável

---

## ⚠️ Aviso Legal

> Esta ferramenta foi desenvolvida **estritamente para fins educacionais** e para a realização de avaliações de segurança em **sistemas devidamente autorizados**. O uso não autorizado contra sistemas de terceiros é ilegal e antiético. O desenvolvedor não se responsabiliza pelo uso indevido desta ferramenta.

**Use com responsabilidade. Só escaneie o que você tem permissão para escanear.**


---
<div align="center">
  
Desenvolvido por **[@Liragbr](https://github.com/Liragbr)**


---
</div>
