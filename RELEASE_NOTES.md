Demo de três capítulos: Sala de Contos Infantis, Arquivo dos Versos e Mapas e A Última Página.

**Para abrir no VS Code, baixe `Tinta-e-Esquecimento-Fonte.zip`.** Extraia tudo, instale Python 3.12 de 64 bits e as extensões Python e Python Debugger da Microsoft, execute `preparar_windows.bat` uma vez, abra a pasta que contém `main.py` no VS Code e pressione F5. A preparação no Windows cria `.venv` e instala Pygame; precisa de internet na primeira vez. `jogar.bat` também prepara e executa o jogo. As instruções estão em `COMECAR_NO_VSCODE.txt`.

**Para jogar sem instalar Python, baixe `Tinta-e-Esquecimento-Windows.zip`.** Extraia tudo e execute `TintaEEsquecimento.exe`, preservando `assets` e `_internal`. O executável não tem assinatura digital e pode ser bloqueado pelo software de segurança. Mantenha a proteção ativa e registre o texto do alerta para investigação; o pacote Fonte permite executar por Python sem liberar o executável. Esta atualização não garante a resolução de um bloqueio de antivírus.

Inclui menu com controles, tinta e leitura, rabisco, lança, escudo, pontes temporárias, chefe, vitória, derrota e assinatura final. Mantém o personagem animado, três fundos e três sons enviados pelo usuário, com licenças e adaptações em `CREDITOS.md`.

A inicialização agora informa erros e grava um diagnóstico local. A build inclui hashes SHA-256 dos dois ZIPs em `SHA256SUMS.txt` para conferir a integridade dos arquivos. O workflow verifica o pacote Fonte e seus scripts no Windows, executa os testes e faz uma abertura automatizada do executável com vídeo/áudio simulados. Teclado, som e bloqueios no computador de destino ainda precisam de verificação local.
