# GeoCDCI - Automação Geográfica da Certidão de Dados Cadastrais do Imóvel

### Secretaria Municipal da Fazenda - SF
### Subsecretaria da Receita Municipal - SUREM
### Departamento de Cadastros - DECAD
### Divisão do Mapa de Valores - DIMAP

O GeoCDCI é um sistema desenvolvido para processar e validar a localização de imóveis no território do Município de São Paulo com o objetivo de emitir a Certidão de Dados Cadastrais do Imóvel (CDCI) ou a Certidão de Inexistência de Lançamento. O sistema utiliza integração via WFS (Web Feature Service) com as bases geográficas oficiais para confrontar as informações declaradas pelo munícipe com o Cadastro Imobiliário Fiscal, conforme os ritos estabelecidos na Ordem Interna SF/SUREM nº 07/2018.

O valor gerado por este sistema consiste na automação da emissão de certidões que, anteriormente, dependiam de análise técnica manual para a identificação inequívoca do imóvel, reduzindo o tempo de resposta ao cidadão e a carga processual nas unidades administrativas.

---

## Breve descrição do funcionamento do sistema

O sistema opera através de um motor de geoprocessamento que realiza a geolocalização de endereços em múltiplos níveis, iniciando pela busca em bases de endereços oficiais e progredindo para a interpolação linear em eixos de logradouros. A aplicação permite o ajuste fino da localização pelo cidadão no mapa, validando a posição contra polígonos de lotes e áreas de restrição cadastral em tempo real para a classificação automática da certidão de acordo com a norma vigente.

---

## Jornada do usuário detalhada e regras de negócio principais

O funcionamento do sistema segue as etapas e critérios de validação descritos abaixo:

### 1. Entrada de Dados
O munícipe informa obrigatoriamente o logradouro e o número do imóvel. O sistema fornece orientações sobre a definição de logradouro para reduzir erros de preenchimento.

### 2. Validação por Base de Endereços Oficiais
O sistema executa uma busca por similaridade (fuzzy search) na base de endereços cadastrados no IPTU:
*   **Correspondência Exata:** O sistema encerra o fluxo e emite a certidão positiva.
*   **Correspondência Parcial:** São oferecidas as 5 melhores sugestões. Caso o usuário selecione uma, o fluxo é encerrado com a emissão da certidão. Caso contrário, inicia-se o georreferenciamento.

### 3. Identificação de Logradouro e Segmentos
Busca do logradouro em base local de eixos de vias:
*   **Identificação Positiva:** O sistema recupera os IDs dos segmentos de reta vinculados.
*   **Sugestão de Vias:** Apresentação de até 5 matches para seleção do usuário.
*   **Insucesso na Busca:** Direcionamento para análise manual via SP156.

### 4. Geocodificação por Interpolação
O ponto geográfico é definido com base na numeração dos segmentos de reta:
*   **Numeração Localizada:** O ponto é posicionado proporcionalmente entre o início e o fim do segmento identificado.
*   **Numeração Não Localizada:** O ponto é posicionado no centro do segmento de numeração central do logradouro.

### 5. Confirmação Espacial de Proximidade
Exibição de mapa interativo com os 5 lotes mais próximos ao ponto gerado:
*   **Confirmação de Lote:** O usuário seleciona o polígono correto e o sistema emite a certidão positiva.
*   **Ajuste de Posição:** Caso o lote não seja identificado, o sistema permite o deslocamento manual do ponto.

### 6. Ajuste Manual e Validação Territorial Final
O ajuste manual é restrito a um raio de 50 metros (configurável via ambiente) a partir da geocodificação inicial:
*   **Áreas Impeditivas:** Se o ponto for posicionado em logradouros públicos ou áreas protegidas, o sistema emite certidão negativa ou indeferimento.
*   **Contenção Direta:** Caso o ponto esteja dentro de um lote, a certidão positiva é gerada para o registro correspondente.
*   **Sugestão de Vizinhança:** Caso não haja contenção, o sistema oferece os 5 lotes mais próximos à nova posição para confirmação final do usuário antes de, em caso de novo insucesso, encaminhar ao atendimento manual.

---

Este é um software livre licenciado sob a **GNU Affero General Public License v3.0 (AGPL v3)**.
