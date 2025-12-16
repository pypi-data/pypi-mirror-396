from django.db import models
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.blocks import StructBlock, BooleanBlock, CharBlock
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from django.utils.html import strip_tags
from wagtail.search import index
from enap_designsystem.blocks.semana_blocks import (
    BRAND_INOVACAO_CHOICES, 
    BRAND_TEXTS_CHOICES,
    BRAND_BG_CHOICES, 
    BRAND_BUTTON_CHOICES, 
    BRAND_HOVER_CHOICES,
)

from enap_designsystem.blocks.html_blocks import BACKGROUND_COLOR_CHOICES, FONTAWESOME_ICON_CHOICES

from .html_blocks import ApresentacaoCardBlock, CardBlock, NumeroCardBlock, CardBlockInfo, LinkBlock



class MenuNavBlock(blocks.StructBlock):
    """Bloco para menu de navegação customizado"""
    
    items_menu = blocks.ListBlock(
        blocks.StructBlock([
            ('texto', blocks.CharBlock(max_length=50, help_text="Texto do menu")),
            ('url', blocks.URLBlock(required=False, help_text="URL externa")),
            ('pagina_interna', blocks.PageChooserBlock(required=False, help_text="Ou escolha uma página interna")),
            ('ativo', blocks.BooleanBlock(required=False, default=False, help_text="Marcar como item ativo")),
        ]),
        min_num=1,
        max_num=10,
        help_text="Itens do menu de navegação"
    )
    
    logo = ImageChooserBlock(
        required=False,
        help_text="Imagem de logo da esquerda"
    )
    
    logo_url = blocks.URLBlock(
        required=False,
        help_text="Link ao clicar na logo"
    )
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor de fundo do menu"
    )
    
    cor_texto = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        default='#F8F9FA',
        help_text="Cor do texto do menu",
        required=False
    )
    
    cor_ativo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do item ativo"
    )
    
    cor_hover = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do hover nos itens"
    )

    class Meta:
        template = 'enap_designsystem/semana_inovacao/blocks_menu_navigation.html'
        icon = 'list-ul'
        label = 'Menu de Navegação'



class VideoHeroBlock(blocks.StructBlock):
    
    background_image = ImageChooserBlock(required=False, help_text="Imagem de fundo para o banner.")
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',  # Cinza claro ENAP
        help_text="Cor de fundo do componente"
    )
    
    altura_banner = blocks.CharBlock(required=False, help_text="Altura do banner (ex: 600px, 80vh).")
    
    video_file = DocumentChooserBlock(
        label="Arquivo de vídeo",
        required=False,
        help_text="Upload direto do arquivo de vídeo (MP4, WebM, etc.)"
    )
    
    titulo = blocks.RichTextBlock(required=False, help_text="Titulo")
    
    subtitulo = blocks.RichTextBlock(required=False, help_text="Subtítulo com suporte a formatação.")
    
    logo = ImageChooserBlock(required=False, help_text="Logo sobre o banner.")

    class Meta:
        template = "componentes_variaveis/video_hero_banner.html"
        icon = "media"
        label = "Banner com vídeo"
        label_format = "Banner com vídeo: {titulo_banner}"



class PainelBlock(blocks.StructBlock):
    """
    Componente simples de apresentação com título, texto e botão
    Reutilizável para diferentes seções
    """
    
    # Cor de fundo da seção
    cor_fundo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor de fundo do componente"
    )
    
    # Título
    titulo = blocks.CharBlock(
        required=True,
        max_length=100,
        help_text="Título principal"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do título"
    )

    cor_texto = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do texto"
    )
    
    # Quadrado de conteúdo
    cor_quadrado = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor de fundo do quadrado de conteúdo"
    )
    
    conteudo = blocks.RichTextBlock(
        required=True,
        help_text="Conteúdo do quadrado (rich text)"
    )
    
    # Botão
    botao_texto = blocks.CharBlock(
        required=False,
        max_length=50,
        help_text="Texto do botão"
    )
    
    botao_url = blocks.URLBlock(
        required=False,
        help_text="URL de destino do botão"
    )
    
    botao_icone = blocks.ChoiceBlock(
        choices=FONTAWESOME_ICON_CHOICES,
        required=False,
        default='',
        help_text="Ícone do botão"
    )
    
    cor_botao = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do botão"
    )
    
    cor_botao_hover = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do botão no hover"
    )
    
    cor_botao_active = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do botão ao apertar"
    )
    
    class Meta:
        template = 'componentes_variaveis/painel.html'
        icon = 'doc-full'
        label = 'Painel Informativo'
        help_text = 'Painel Informativo: Cabeçalho, corpo e botão'
        label_format = "Painel Informativo: {titulo_banner}"



class PainelCardsBlock(blocks.StructBlock):
    """
    Componente simples de apresentação com título, texto e grid de cards
    """
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#6A1B9A', 
        help_text="Cor de fundo do componente"
    )
    
    titulo = blocks.CharBlock(
        required=True,
        max_length=200,
        help_text="Título principal"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do título"
    )
    
    cor_quadrado = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor de fundo do quadrado de conteúdo"
    )
    
    conteudo = blocks.RichTextBlock(
        required=True,
        help_text="Conteúdo descritivo (rich text)"
    )
    
    cor_texto = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do texto do conteúdo"
    )
    
    # Grid de cards
    grid_tipo = blocks.ChoiceBlock(
        choices=[
            ('cards-grid-1', '1 card por linha'),
            ('cards-grid-2', 'Até 2 cards'),
            ('cards-grid-3', 'Até 3 cards'),
            ('cards-grid-4', 'Até 4 cards'),
            ('cards-grid-5', 'Até 5 cards')
        ],
        default='cards-grid-5',
        help_text="Quantos cards por linha",
        label="Cards por linha"
    )

    # Lista de cards
    cards = blocks.StreamBlock([
        ('card_apresentacao',  ApresentacaoCardBlock()),
    ], 
    required=False,
    help_text="Cards da seção de apresentação",
    label="Cards"
    )

    class Meta:
        template = 'componentes_variaveis/painelinfo.html'
        icon = 'doc-full'
        label = 'Painel Informativo: título principal, texto explicativo e cards com ícones'
        help_text = 'Painel Informativo Cards: título principal, texto explicativo e cards com ícones'
        label_format = "Painel Informativo Cards: {titulo_banner}"



class SecaoPainelCardsBlock(blocks.StructBlock):
    """
    Seção de apresentação com título, conteúdo e grid de cards
    """
    imagem_fundo = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo"
    )

    cor_fundo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor de fundo do componente"
    )
    
    cor_fundo_cards = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor de fundo dos cards"
    )
    
    titulo = blocks.CharBlock(
        required=False,
        max_length=200,
        help_text="Título da seção"
    )

    subtitulo = blocks.RichTextBlock(
        required=False,
        help_text="Subtítulo da seção"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do título"
    )
    
    cor_subtitulo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do subtítulo"
    )

    link_url = blocks.URLBlock(
        label="URL do Link",
        required=False,
        help_text="Link para página externa ou interna"
    )
    
    link_text = blocks.CharBlock(
        label="Texto do Link",
        max_length=50,
        required=False,
        default="Saiba mais",
        help_text="Texto que aparecerá no botão/link"
    )
    
    cor_botao = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do botão"
    )
    
    cor_botao_hover = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do botão no hover"
    )
    
    cor_botao_active = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do botão ao apertar"
    )

    cor_botao_texto = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do texto do botão"
    )
    
    link_target = blocks.ChoiceBlock(
        label="Abrir link em",
        choices=[
            ('_self', 'Mesma janela'),
            ('_blank', 'Nova janela'),
        ],
        default='_self',
        required=False
    )

    # Layout dos cards
    layout_cards = blocks.ChoiceBlock(
        choices=[
            ('cards-1-coluna', '1 card por linha'),
            ('cards-2-colunas', 'Até 2 cards por linha'),
            ('cards-3-colunas', 'Até 3 cards por linha'),
            ('cards-4-colunas', 'Até 4 cards por linha'),
            ('cards-5-colunas', 'Até 5 cards por linha')
        ],
        default='cards-5-colunas',
        help_text="Layout da grade de cards",
        label="Layout dos cards"
    )
    
    posicao_cards = blocks.ChoiceBlock(
        choices=[
            ('flex-start', 'Esquerda'),
            ('center', 'Centro'),
            ('flex-end', 'Direita')
        ],
        default='center',
        help_text="Posição dos cards (Funciona apenas com 1 card por linha)",
        label="Posição dos cards"
    )
    
    # Stream de cards
    cards = blocks.StreamBlock([
        ('card', CardBlockInfo()),
    ], 
    required=False,
    help_text="Adicione quantos cards precisar"
    )

    class Meta:
        template = 'componentes_variaveis/cards_blocks_info.html'
        icon = 'doc-full'
        label = 'Seção com título & cards'
        help_text = 'Seção com título & cards'
        label_format = "Seção com título & cards: {titulo_banner}"



class BigNumbers(blocks.StructBlock):
    """
    Componente de apresentação de números/estatísticas
    """
    
    cor_fundo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor de fundo do componente"
    )
    
    titulo = blocks.CharBlock(
        required=True,
        max_length=200,
        help_text="Título principal da seção (ex: Nossos números)"
    )
    
    cor_titulo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',  
        help_text="Cor do título"
    )
    
    # Quadrado de conteúdo
    cor_fundo_conteudo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor de fundo do quadrado de conteúdo"
    )

    cor_line = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#F8F9FA',
        help_text="Cor do da linha debaixo",
    )
    
    # Lista de cards de números
    lista_numeros = blocks.ListBlock(
        NumeroCardBlock(),
        min_num=1,
        max_num=20,
        help_text="Adicione os cards de números/estatísticas"
    )
    
    # Configurações adicionais do grid
    espacamento_cards = blocks.ChoiceBlock(
        choices=[
            ('spacing-sm', 'Espaçamento pequeno'),
            ('spacing-md', 'Espaçamento médio'),
            ('spacing-lg', 'Espaçamento grande'),
        ],
        default='spacing-md',
        help_text="Espaçamento entre os cards"
    )
    
    tamanho_cards = blocks.ChoiceBlock(
        choices=[
            ('card-sm', 'Cards pequenos'),
            ('card-md', 'Cards médios'),
            ('card-lg', 'Cards grandes'),
        ],
        default='card-md',
        help_text="Tamanho dos cards"
    )
    
    bordas_arredondadas = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Cards com bordas arredondadas"
    )
    
    class Meta:
        template = 'componentes_variaveis/big_numbers.html'
        icon = 'snippet'
        label = 'Sessão para números e estatísticas importantes'
        help_text = 'Sessão para números e estatísticas importantes'
        label_format = "Sessão para números e estatísticas importantes"






class FooterGenericoColum(StructBlock):
    """Block para footer genérico"""
    
    # Configurações gerais
    cor_fundo = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#525258',
        label="Cor do fundo", 
        help_text="Selecione a cor de fundo do footer"
    )
    
    cor_texto = blocks.ChoiceBlock(
        choices=BACKGROUND_COLOR_CHOICES,
        required=False,
        default='#FFFFFF',
        label="Cor dos textos", 
        help_text="Selecione a cor dos textos do footer"
    )
    
    # Seção de logo
    logo = ImageChooserBlock(
        label="Logo", 
        required=False,
        help_text="Selecione a logo para o footer"
    )
    
    texto_logo = blocks.RichTextBlock(
        label="Texto abaixo da logo", 
        help_text="Texto que fica abaixo da logo", 
        required=False,
        features=['bold', 'italic', 'link']
    )
    
    # Primeira seção de links
    titulo_1 = blocks.CharBlock(
        required=False,
        max_length=100,
        label="Título da primeira seção",
        help_text="Título da primeira coluna de links"
    )
    
    links_1 = blocks.StreamBlock([
        ('link', LinkBlock()),
    ], 
        required=False,
        label="Links da primeira seção",
        help_text="Adicione links para a primeira coluna"
    )
    
    # Segunda seção de links
    titulo_2 = blocks.CharBlock(
        required=False,
        max_length=100,
        label="Título da segunda seção",
        help_text="Título da segunda coluna de links"
    )
    
    links_2 = blocks.StreamBlock([
        ('link', LinkBlock()),
    ], 
        required=False,
        label="Links da segunda seção",
        help_text="Adicione links para a segunda coluna"
    )
    
    # Terceira seção de links
    titulo_3 = blocks.CharBlock(
        required=False,
        max_length=100,
        label="Título da terceira seção",
        help_text="Título da terceira coluna de links"
    )
    
    links_3 = blocks.StreamBlock([
        ('link', LinkBlock()),
    ], 
        required=False,
        label="Links da terceira seção",
        help_text="Adicione links para a terceira coluna"
    )

    class Meta:
        template = 'enap_designsystem/blocks/footer_block.html'
        icon = 'footer'
        label = 'Rodapé (Footer)'
        help_text = 'Adicione um footer personalizado com links organizados em colunas'
        label_format = "Rodapé (Footer)"




BODY_BLOCKS_FLEX = [
    ('menu_navegacao', MenuNavBlock()),
    ('video_hero', VideoHeroBlock()),
    ('painel_informativo', PainelBlock()),
    ('painel_cards', PainelCardsBlock()),
    ('secao_painel_cards', SecaoPainelCardsBlock()),
    ('big_numbers', BigNumbers()),
    ('footer_generico_block', FooterGenericoColum()),
]



