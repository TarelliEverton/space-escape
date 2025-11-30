🚀 Space Escape - Arcade Edition

Um jogo estilo arcade desenvolvido em Python com Pygame onde você deve desviar dos meteoros e sobreviver o máximo possível!

📚 Sobre o Projeto
Este jogo foi desenvolvido como Trabalho Final da disciplina de Algoritmos e Programação ministrada pelo professor @ProfessorFilipo.
O professor nos forneceu uma versão base simplificada do jogo e uma lista de tarefas/melhorias que deveríamos implementar para demonstrar os conhecimentos adquiridos durante a disciplina.

Funcionalidades Implementadas (Tarefas do Trabalho)
A partir da versão inicial, foram adicionadas as seguintes melhorias:

✅ Tela inicial estilo Arcade "Insert Coin"
✅ Adicinar 3 fases com 3 niveis de dificultade
✅ fazer com que a imagem de fundo mude conforme muda a dificuldade ou
fase do jogo
✅ Sistema de trilha sonora por fase (músicas diferentes para cada fase)
✅ Opção multiplayer (tecla AWSD E SETAS)
✅ Campeonato multiplaer com tela de vitória
✅ Opção jogar com o mouse
✅ Meteoro especial (Estrela de Nêutrons) que causa -2 vidas
✅ Meteoro Coração que concede +2 vidas
✅ Buraco Negro (teleporte + invencibilidade temporária)
✅ Sistema de tiros para destruir meteoros
✅ Tela de vitória para modo Multiplayer
✅ Tela de fim de jogo com animações

🎮 Como Jogar

### Requisitos
- Python 3.8 ou superior
- Pygame 2.0 ou superior

### Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/TarelliEverton/space-escape.git
cd space-escape
```

2. **Instale as dependências:**
```bash
pip install pygame
```

3. **Execute o jogo:**
```bash
python space_escape.py
```

🕹️ Controles

### Modo Um Jogador (Mouse)
| Ação | Controle |
|------|----------|
| Mover | Mouse |
| Atirar | Clique Esquerdo |

### Modo Um Jogador (Teclado)
| Ação | Controle |
|------|----------|
| Mover | W A S D |
| Atirar | Espaço |

### Modo Dois Jogadores
| Jogador | Mover | Atirar |
|---------|-------|--------|
| Player 1 | W A S D | Espaço |
| Player 2 | Setas | Ctrl |

⚡ Power-ups e Obstáculos

| Item | Efeito | Cor |
|------|--------|-----|
| Meteoro Normal | -1 Vida | Vermelho |
| Meteoro Especial | -2 Vidas | Azul/Ciano |
| Meteoro Coração | +2 Vidas | Rosa |
| Buraco Negro | Teleporte + Escudo 4s | Roxo |

🎯 Sistema de Fases

| Fase | Pontuação | Velocidade |
|------|-----------|------------|
| Fase 1 | 0 - 99 pts | Normal |
| Fase 2 | 100 - 299 pts | Rápida |
| Fase 3 | 300+ pts | Muito Rápida |

Cada fase possui sua própria trilha sonora!

🏆 Funcionalidades

- ✅ Modo Single Player (Mouse ou Teclado)
- ✅ Modo Multiplayer Local (2 jogadores)
- ✅ Sistema de High Scores (salvo em JSON)
- ✅ 3 Fases com dificuldade progressiva
- ✅ Trilha sonora diferente por fase
- ✅ Power-ups variados
- ✅ Sistema de tiros
- ✅ Tela inicial estilo Arcade
- ✅ Animações e efeitos visuais

📁 Estrutura de Arquivos

```
space-escape/
├── space_escape.py          # Código principal do jogo
├── README.md                 # Este arquivo
├── highscores.json          # Salvo automaticamente
│
├── # IMAGENS
├── ceu.png                   # Fundo do jogo
├── nave001.png               # Sprite da nave
├── meteoro001.png            # Sprite do meteoro
├── projetil.png              # Sprite do projétil
├── neutron-star_spritesheet_medium.png
├── buraco_negro_spritesheet.png
├── heart-meteor_spritesheet_medium.png
│
└── # SONS
    ├── game-gaming-background-music-385611.mp3  # Música Fase 1
    ├── musicaFase2.mp3                          # Música Fase 2
    ├── musicaFase3.mp3                          # Música Fase 3
    ├── som_projetil.mp3                         # Som do tiro
    ├── classic-game-action-positive-5-224402.mp3
    └── stab-f-01-brvhrtz-224599.mp3
```


👨‍🏫 Autor

**Prof. Filipo Novo Mor**
- GitHub: [@TarelliEverton](https://github.com/TarelliEverton)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

⭐ Se gostou do projeto, deixe uma estrela no repositório!
