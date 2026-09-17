# Prompt para mockups do comm-welcome

Crie mockups visuais detalhados para o comm-welcome, um novo aplicativo de boas-vindas da distribuição Linux BigCommunity.

O objetivo desta etapa é definir a aparência e a experiência de uso. Não implemente código. Produza imagens das telas, acompanhadas de uma explicação curta das decisões visuais.

## Contexto do produto

O comm-welcome recebe principalmente pessoas que acabaram de instalar o BigCommunity. Deve apresentar o sistema, ajudar a descobrir aplicativos próprios e oferecer acesso à personalização, navegadores e ajuda.

A implementação será obrigatoriamente em Python + GTK4 + libadwaita.

O design precisa ser viável com componentes reais desse toolkit. Deve parecer um aplicativo Linux de desktop bem acabado, com identidade BigCommunity.

Use português brasileiro nos mockups.

## Direção visual

- Aparência acolhedora, moderna e organizada.
- Hierarquia clara, bom espaçamento e poucos elementos disputando atenção.
- Componentes e proporções coerentes com GTK4/libadwaita.
- Cantos arredondados, bordas discretas e sombras suaves.
- Ícones reconhecíveis dos aplicativos.
- Identidade BigCommunity no cabeçalho de apresentação.
- Caso não tenha acesso ao logotipo oficial, use um espaço claramente reservado para ele.
- Cores de destaque moderadas, sem depender de cores para comunicar estados.
- Evite grandes áreas decorativas que empurrem as ações para fora da tela.
- Evite aparência de painel administrativo, página comercial ou dashboard com métricas.
- Evite efeitos de vidro, transparências intensas e controles difíceis de reproduzir em libadwaita.

A aplicação deve respeitar os temas claro e escuro. Mostre as duas versões com contraste adequado.

## Estrutura de navegação

Proponha uma navegação simples entre:

1. Boas-vindas
2. Aplicativos
3. Navegadores
4. Ajuda

Escolha um componente de navegação adequado ao libadwaita. Em uma janela pequena, a navegação deve se adaptar sem comprimir excessivamente o conteúdo.

Evite uma barra lateral larga e permanente que desperdice espaço.

## Tela 1 — Boas-vindas

Conteúdo:

Título:
“Boas-vindas ao BigCommunity”

Subtítulo:
“Seu novo sistema, do seu jeito.”

Apresentação curta:
“Conheça os aplicativos, personalize seu ambiente e encontre o que precisa para começar.”

No GNOME, exiba um cartão principal para o Big Gnome Center:

Título:
“Deixe o desktop com a sua cara”

Descrição:
“Explore layouts, temas, painel, dock e opções de personalização.”

Botão:
“Abrir Big Gnome Center”

Esse cartão deve ter mais destaque que os demais, sem ocupar a maior parte da janela.

Abaixo, apresente poucos atalhos para começar, por exemplo:

- Conhecer aplicativos
- Escolher navegador
- Encontrar ajuda

Mostre uma seleção pequena de aplicativos úteis, se houver espaço. O catálogo completo terá sua própria tela.

Inclua a opção:
“Não mostrar novamente”

Texto auxiliar, se necessário:
“Você pode abrir as boas-vindas pelo menu de aplicativos.”

Essa preferência controla apenas a abertura automática. Não bloqueia a reabertura manual.

O fechamento da janela deve ser simples. Não crie um assistente obrigatório com etapas que o usuário precisa concluir.

### Adaptação ao ambiente gráfico

O Big Gnome Center só deve aparecer em sessões GNOME quando estiver instalado.

Em Cinnamon, Xfce e KDE, o destaque pode apresentar a personalização disponível naquele ambiente.

Mostre uma variação compacta da tela inicial para outro ambiente, sem inventar um aplicativo específico.

Aplicativos ausentes ou incompatíveis devem ser omitidos. A tela deve se reorganizar naturalmente.

## Tela 2 — Aplicativos

Apresente os aplicativos em grupos claros, com cartões compactos ou linhas visuais bem organizadas.

Cada item deve ter:

- Ícone do aplicativo.
- Nome legível.
- Descrição curta.
- Botão “Abrir”.

Os botões abrem os aplicativos. Nenhuma configuração será aplicada automaticamente pelo welcome.

Organização sugerida:

### Dia a dia

WebApps
“Use seus sites favoritos como aplicativos.”

BigOCRPDF
“Torne o texto de documentos digitalizados pesquisável e copiável.”

Ashy Terminal
“Explore um terminal com recursos para organizar suas sessões.”

Big Blocks
“Divirta-se com um jogo de encaixar blocos.”

### Áudio e vídeo

Filtro de ruídos
“Reduza ruídos do microfone e do áudio.”

Conversor de áudio
“Converta arquivos de áudio para outros formatos.”

Conversor de vídeo
“Converta seus vídeos para outros formatos.”

Big Recorder
“Grave e organize suas notas de voz.”

### Sistema e família

Ajustes gerais
“Conheça as opções de configuração do sistema.”

Informações de hardware
“Conheça os componentes do computador.”

Gerenciamento de hardware
“Acesse as opções de drivers e kernel.”

Controle parental
“Conheça os recursos de controle de uso do computador.”

Informações de rede
“Consulte detalhes das suas conexões de rede.”

Não coloque todos esses itens na tela inicial. Mostre como a tela de aplicativos organiza o conteúdo sem causar sobrecarga.

## Tela 3 — Escolher navegador

Essa é uma função importante do aplicativo.

Título:
“Qual navegador combina com você?”

Descrição:
“O Brave já está pronto para usar. Se preferir, escolha outro navegador para instalar.”

O Brave é o navegador padrão da distribuição.

Mostre o Brave com os indicadores:
“Instalado”
“Padrão atual”

Seu botão principal deve ser:
“Abrir”

Para os mockups, use estes navegadores como candidatos ilustrativos:

- Brave
- Firefox
- Google Chrome
- Chromium
- Vivaldi
- Opera

A lista final dependerá da disponibilidade de pacotes e dos métodos de instalação aprovados para a distro. Não coloque nomes de repositórios, comandos ou detalhes de empacotamento na interface.

Não invente comparações de desempenho, segurança, privacidade ou compatibilidade. Use descrições neutras e curtas, ou dispense a descrição quando ela não acrescentar informação.

Cada cartão deve mostrar:

- Ícone oficial ou espaço reservado identificável.
- Nome.
- Estado de instalação.
- Ação principal.

### Comportamento da escolha

Para um navegador não instalado, o botão será:
“Escolher e instalar”

O clique deve iniciar imediatamente o fluxo de instalação. Não crie uma etapa separada de seleção seguida de um botão distante para confirmar.

O rótulo precisa deixar claro, antes do clique, que a ação instala um aplicativo.

Pode haver autenticação do sistema quando necessária. Não desenhe um formulário próprio solicitando a senha do usuário dentro do welcome.

O usuário não é obrigado a instalar outro navegador. Inclua uma saída simples, como:
“Continuar com Brave”

Instalar outro navegador não deve remover o Brave.

Instalar e definir como padrão são ações distintas.

Após a instalação, ofereça:
“Abrir”
“Definir como padrão”

Se o navegador já estiver instalado, mostre essas ações diretamente, sem oferecer reinstalação.

O indicador “Padrão atual” deve acompanhar o navegador efetivamente configurado como padrão.

Não use indicadores de seleção que façam parecer que o navegador padrão mudou antes de essa ação ocorrer.

### Estados da instalação

Mostre o fluxo completo com variações visuais:

1. Disponível
   Botão “Escolher e instalar”.

2. Preparando
   Estado “Preparando instalação…”.

3. Aguardando autenticação
   Mensagem curta orientando a concluir a autenticação do sistema.

4. Instalando
   Nome do navegador e progresso.
   Use percentual apenas quando esse dado estiver disponível.
   Caso contrário, mostre um indicador de atividade sem percentual fictício.

5. Concluído
   Mensagem “Firefox instalado”, ou nome correspondente.
   Botões “Abrir” e “Definir como padrão”.

6. Falha
   Mensagem compreensível.
   Ação “Tentar novamente”.
   Detalhes técnicos podem ficar recolhidos em “Ver detalhes”.

7. Sem internet
   Mensagem “Conecte-se à internet para instalar outro navegador.”
   O Brave e outros navegadores já instalados continuam disponíveis para abertura.
   O restante do welcome permanece funcional.

8. Gerenciador de pacotes ocupado
   Mensagem “Outra instalação está em andamento. Tente novamente quando ela terminar.”

Evite múltiplas instalações simultâneas. Durante uma instalação, as outras ações de instalar devem indicar claramente sua indisponibilidade temporária.

O usuário pode navegar pelas outras telas sem perder o progresso.

Não desenhe um botão de cancelamento de instalação sem considerar se o procedimento pode ser interrompido com segurança. Diferencie sair da tela de interromper a operação.

## Tela 4 — Ajuda

Apresente acessos claros para:

- Documentação
- Comunidade
- Suporte

Endereços conhecidos:

Site:
https://communitybig.org/

Fórum:
https://forum.biglinux.com.br/t/biglinuxcommunity

Telegram:
https://t.me/BigLinuxCommunity

O endereço da documentação ainda será confirmado. No mockup, represente essa ação como proposta, sem inventar uma URL.

Indique discretamente quais ações abrem páginas externas e precisam de internet.

Pode haver um grupo pequeno:
“Informações úteis para pedir ajuda”

Com acesso a:

- Informações de hardware
- Informações de rede

Essas ações apenas abrem os aplicativos correspondentes. Não enviam informações automaticamente.

## Responsividade e acessibilidade

Considere:

- Janela principal de aproximadamente 820 × 700 unidades lógicas.
- Uma variação estreita de aproximadamente 460 unidades lógicas de largura.
- Uso em telas de 1366 × 768.
- Escalas de 100%, 150% e 200%.
- Texto ampliado.
- Traduções mais longas que o português.
- Navegação por teclado.
- Foco visível.
- Contraste adequado.
- Leitores de tela.
- Preferência por animações reduzidas.
- Possibilidade de idiomas com escrita da direita para a esquerda.

Nas telas estreitas:

- Cartões passam para uma coluna.
- Textos quebram linha naturalmente.
- Botões continuam acessíveis.
- A navegação se adapta.
- O conteúdo pode rolar verticalmente.
- Não deve existir rolagem horizontal.

## Funcionamento offline

A apresentação, os ícones, as descrições e a descoberta dos aplicativos instalados devem funcionar offline.

Não use imagens remotas ou conteúdo que precise carregar da internet para compor a interface.

A conexão será necessária para instalar navegadores e abrir recursos externos.

## Entregáveis visuais

Produza mockups suficientes para mostrar:

1. Boas-vindas no GNOME, tema claro.
2. Boas-vindas no GNOME, tema escuro.
3. Tela de aplicativos com os grupos propostos.
4. Tela de navegadores, com Brave instalado e padrão.
5. Instalação de outro navegador em andamento.
6. Instalação concluída, com opção de definir como padrão.
7. Estado sem internet e exemplo de falha.
8. Tela de ajuda.
9. Variação estreita da tela inicial e da tela de navegadores.
10. Variação da tela inicial em outro ambiente gráfico.

Mantenha consistência de espaçamento, tipografia, ícones, botões e navegação entre todas as telas.

Apresente primeiro as imagens. Depois explique brevemente:

- A hierarquia visual.
- A navegação.
- A adaptação a telas pequenas.
- A diferença entre instalar um navegador e defini-lo como padrão.

Priorize uma proposta realizável em GTK4/libadwaita, com textos legíveis e aparência de produto pronto.
