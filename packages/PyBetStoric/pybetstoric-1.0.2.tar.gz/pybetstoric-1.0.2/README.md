# PyBetStoric

Biblioteca Python para acessar dados históricos de jogos da Pragmatic Play Live.

## 🚀 Instalação

```bash
pip install PyBetStoric
```

## 📖 Uso Básico

```python
import PyBetStoric

# Definir Login - Deve ser adquirido via telegram 'andremelol' ou via email 'amelo171710@gmail.com '
client = PyBetStoric.PragmaticClient(
    email="seu@email.com",
    user="seu_usuario", 
    password="sua_senha",
    license_code="SEU_CODIGO_ADQUIRIDO"
)

# Acessar jogos
jogos = PyBetStoric.Games(client)

# Obter histórico da roleta
historico = jogos.roleta.get_mega_roulette(number_of_games=50)
print(historico)

# Fechar cliente
client.close()
```

## 🎮 Jogos Disponíveis

### Roleta
- **Mega Roulette**: `jogos.roleta.get_mega_roulette()`
- **Speed Roulette**: `jogos.roleta.get_speed_roulette()`
- **VIP Roulette**: `jogos.roleta.get_vip_roulette()`
- **Auto Roulette**: `jogos.roleta.get_auto_roulette()`
- E mais de 30 variações disponíveis

### Bacará
- **Speed Baccarat**: `jogos.bacara.get_speed_baccarat()`
- **Mega Baccarat**: `jogos.bacara.get_mega_baccarat()`
- **Fortune 6 Baccarat**: `jogos.bacara.get_fortune_6_baccarat()`
- **VIP Baccarat**: `jogos.bacara.get_vip_baccarat()`
- E mais de 40 variações disponíveis

### Game Shows
- **Sweet Bonanza**: `jogos.game_shows.get_sweet_bonanza()`
- **Money Time**: `jogos.game_shows.get_money_time()`
- **Dice City**: `jogos.game_shows.get_dice_city()`
- **Boom City**: `jogos.game_shows.get_boom_city()`

### Jogos Brasileiros
- **Roleta Brasileira**: `jogos.jogos_brasileiros.get_roleta_brasileira()`
- **Baccarat Brasileiro**: `jogos.jogos_brasileiros.get_baccarat_brasileiro()`

### Jogos Asiáticos
- **Dragon Tiger**: `jogos.jogos_asiaticos.get_dragon_tiger()`
- **Andar Bahar**: `jogos.jogos_asiaticos.get_andar_bahar()`

### Crash
- **Spaceman**: `jogos.crash.get_spaceman()`

## 📊 Exemplos de Uso

### Obter múltiplos jogos
```python
import PyBetStoric

client = PyBetStoric.PragmaticClient(
    email="seu@email.com",
    user="seu_usuario",
    password="sua_senha", 
    license_code="SEU_CODIGO"
)

jogos = PyBetStoric.Games(client)

# Obter dados de diferentes jogos
mega_roulette = jogos.roleta.get_mega_roulette(number_of_games=100)
speed_baccarat = jogos.bacara.get_speed_baccarat(number_of_games=50)
sweet_bonanza = jogos.game_shows.get_sweet_bonanza(number_of_games=25)

print(f"Mega Roulette: {len(mega_roulette)} jogos")
print(f"Speed Baccarat: {len(speed_baccarat)} jogos")
print(f"Sweet Bonanza: {len(sweet_bonanza)} jogos")

client.close()
```

### Análise de dados
```python
import PyBetStoric

client = PyBetStoric.PragmaticClient(
    email="seu@email.com",
    user="seu_usuario",
    password="sua_senha",
    license_code="SEU_CODIGO"
)

jogos = PyBetStoric.Games(client)

# Obter histórico da roleta
historico = jogos.roleta.get_mega_roulette(number_of_games=200)

# Analisar resultados
numeros = [jogo['numero'] for jogo in historico]
cores = [jogo['cor'] for jogo in historico]

print(f"Números mais frequentes: {max(set(numeros), key=numeros.count)}")
print(f"Cor mais frequente: {max(set(cores), key=cores.count)}")

client.close()
```

## ⚡ Recursos

- Acesso a mais de 100 jogos diferentes
- Dados históricos em tempo real
- Suporte a múltiplos jogos simultâneos
- Interface simples e intuitiva

## 🛠️ Requisitos

- Python 3.7+
- Conexão com internet
- Licença válida

## 💡 Dicas

- Use `number_of_games` para controlar quantos jogos históricos obter
- Sempre feche o cliente com `client.close()` após o uso
- Mantenha suas credenciais seguras
- Verifique se sua licença está ativa

## 🔧 Parâmetros Comuns

Todos os métodos de jogos aceitam o parâmetro:
- `number_of_games` (int): Número de jogos históricos a obter (padrão: 100)

## � Lisota Completa de Jogos

Para ver todos os jogos disponíveis com descrições detalhadas, consulte [JOGOS.md](JOGOS.md).

## 🌟 Contribuindo

### Branches do GitHub

- `main`: Branch principal com código estável
- `develop`: Branch de desenvolvimento com novas features
- `feature/*`: Branches para desenvolvimento de novas funcionalidades
- `hotfix/*`: Branches para correções urgentes
- `release/*`: Branches para preparação de releases

### Como Contribuir

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Padrões de Código

- Siga PEP 8 para formatação
- Adicione testes para novas funcionalidades
- Documente suas funções e classes
- Use type hints quando possível

## 🙏 Agradecimentos

Agradecemos especialmente à incrível **comunidade Python** que torna projetos como este possíveis:

- **Python Software Foundation** - Por manter e desenvolver a linguagem Python
- **PyPI** - Por fornecer a infraestrutura de distribuição de pacotes
- **Contribuidores do Requests** - Pela excelente biblioteca HTTP
- **Equipe do Playwright** - Por facilitar a automação web
- **Desenvolvedores do asyncio** - Por tornar a programação assíncrona acessível
- **Comunidade Stack Overflow** - Por compartilhar conhecimento e soluções
- **Mantenedores de bibliotecas open source** - Por dedicarem seu tempo ao ecossistema Python

Um agradecimento especial a todos os desenvolvedores que contribuem para o ecossistema Python, desde bibliotecas fundamentais até ferramentas de desenvolvimento. Vocês tornam o Python uma das linguagens mais poderosas e acessíveis do mundo!

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para dúvidas sobre uso da biblioteca, consulte a documentação ou entre em contato através dos canais oficiais.