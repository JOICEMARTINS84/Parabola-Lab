import math
import random
from fractions import Fraction
import numpy as np
import plotly.graph_objects as go
import streamlit as st

def desafios(textos, status):
    st.subheader('Desafios de investigação')
    for i, (texto, cumprido) in enumerate(zip(textos, status), 1):
        if cumprido:
            st.success(f'{i}. {texto} — condição satisfeita')
        else:
            st.write(f'{i}. {texto}')

OPCOES_A = [-3, -2.5, -2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, 2.5, 3]
AZUL = '#1557C0'
VERDE = '#15803D'
LARANJA = '#B77900'
ROSA = '#DB2777'


def fmt(valor):
    """Inteiros sem decimais; decimais sem zeros finais."""
    valor = float(valor)
    if valor == 0:
        return '0'
    if valor.is_integer():
        return str(int(valor))
    texto = f'{valor:.6f}'.rstrip('0').rstrip('.')
    if float(texto) == 0 or abs(valor) >= 1e12:
        texto = f'{valor:.6g}'
    return texto


def rotulo_latex(valor):
    texto = fmt(valor)
    if 'e' in texto:
        mantissa, expoente = texto.split('e')
        return rf'{mantissa}\times 10^{{{int(expoente)}}}'
    return texto


def num(v):
    if v == 0:
        return '0'
    return np.format_float_positional(float(v), trim='-')


def latex_funcao(a, b, c):
    termos = ['x^2' if a == 1 else '-x^2' if a == -1 else num(a)+'x^2']
    for v, x in [(b, 'x'), (c, '')]:
        if v:
            termos.append(('+' if v > 0 else '-') + ('' if x and abs(v)==1 else num(abs(v))) + x)
    return 'f(x)=' + ''.join(termos)


def calcular(a, b, c):
    # Os valores decimais digitados são tratados como racionais exatos
    # para evitar um discriminante negativo por arredondamento binário.
    af, bf, cf = (Fraction(str(v)) for v in (a, b, c))
    df = bf*bf - 4*af*cf
    delta = float(df)
    xv, yv = float(-bf/(2*af)), float(-df/(4*af))
    if df > 0:
        # Forma numericamente estável da fórmula de Bhaskara.
        q = -0.5*(b + math.copysign(math.sqrt(delta), b))
        raizes = sorted([q/a, c/q])
    elif df == 0:
        raizes = [xv]
    else:
        raizes = []
    return delta, xv, yv, raizes


def passo_grade(span):
    bruto = max(span / 14, 1e-12)
    base = 10**math.floor(math.log10(bruto))
    return next((base*k for k in (1, 2, 5, 10) if base*k >= bruto), 10*base)


def resultado_latex(valor):
    """Usa aproximação quando o arredondamento altera o valor."""
    sinal = '=' if float(fmt(valor)) == valor else r'\approx'
    return sinal + ' ' + rotulo_latex(valor)


def criar_grafico(a, b, c, xv, yv, raizes, escala_real=True):
    lim_x = max(5.0, abs(xv)+3, *[abs(r)+2 for r in raizes])
    ymin, ymax = min(yv, 0.0, c), max(yv, 0.0, c)
    span = max(ymax-ymin, 4.0)
    ymin, ymax = (ymin-0.25*span, ymax+span) if a > 0 else (ymin-span, ymax+0.25*span)
    xmin, xmax = -lim_x, lim_x
    x = np.unique(np.r_[np.linspace(xmin, xmax, 1800), xv, 0, raizes])
    # Mesma graduação nos eixos, com espaçamento adaptado à extensão.
    passo = passo_grade(max(xmax-xmin, ymax-ymin))
    if passo < 1:
        passo = 1
    fig = go.Figure()
    y = a*x**2 + b*x + c
    # Realce do sinal: verde acima do eixo x, vermelho abaixo.
    cortes = [xmin] + raizes + [xmax]
    for j, (inicio, fim) in enumerate(zip(cortes, cortes[1:])):
        if fim <= inicio:
            continue
        xx = np.linspace(inicio, fim, 500)
        yy = a*xx**2 + b*xx + c
        positivo = (a > 0) if len(raizes) != 2 or j != 1 else (a < 0)
        fig.add_trace(go.Scatter(
            x=xx, y=yy, mode='lines', line=dict(width=0),
            fill='tozeroy', fillcolor='rgba(21,128,61,0.12)' if positivo else 'rgba(185,28,28,0.12)',
            showlegend=False, hoverinfo='skip'
        ))
    hover = [[fmt(u), fmt(v)] for u, v in zip(x, y)]
    fig.add_trace(go.Scatter(
        x=x, y=y, customdata=hover,
        mode='lines', name='Parábola',
        line=dict(color=AZUL, width=3.5),
        hovertemplate='x=%{customdata[0]}<br>f(x)=%{customdata[1]}<extra></extra>'
    ))
    fig.add_vline(x=xv, line_dash='dash', line_color=LARANJA, line_width=1.5)
    fig.add_trace(go.Scatter(
        x=[xv], y=[yv], mode='markers+text', name='Vértice',
        text=[f'<b>V {"≈ " if any(float(fmt(v)) != v for v in (xv, yv)) else ""}({fmt(xv)}; {fmt(yv)})</b>'],
        textposition='middle right',
        textfont=dict(color='#875400', size=16),
        hovertemplate=f'Vertice: ({fmt(xv)}; {fmt(yv)})<extra></extra>',
        marker=dict(color=LARANJA, size=14, line=dict(color='white', width=1.5))
    ))
    fig.add_trace(go.Scatter(
        x=[0], y=[c], mode='markers', name='Interseção com y',
        hovertemplate=f'Interseção: (0; {fmt(c)})<extra></extra>',
        marker=dict(color=ROSA, size=12, line=dict(color='white', width=1.5))
    ))
    if raizes:
        fig.add_trace(go.Scatter(
            x=raizes, y=[0]*len(raizes), mode='markers+text', name='Raízes',
            text=[f'<b>x{i+1} {"=" if float(fmt(r)) == r else "≈"} {fmt(r)}</b>' for i, r in enumerate(raizes)],
            textposition='top center', textfont=dict(color='#12613A', size=16),
            customdata=[fmt(r) for r in raizes],
            hovertemplate='Raiz: %{customdata}<extra></extra>',
            marker=dict(color=VERDE, size=13, line=dict(color='white', width=1.5))
        ))
    fig.update_layout(
        template='plotly_white', paper_bgcolor='white', plot_bgcolor='white',
        height=640, font=dict(family='Arial', size=15, color='#173B70'),
        margin=dict(l=70, r=35, t=85, b=65),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0, font=dict(size=14, color='#173B70')),
        xaxis_title=dict(text='<b>x</b>', font=dict(size=19, color='#12366C')),
        yaxis_title=dict(text='<b>y</b>', font=dict(size=19, color='#12366C')),
        hoverlabel=dict(bgcolor='white', font=dict(size=15, color='#12366C')),
        hovermode='closest'
    )
    grade = dict(
        showgrid=True, gridcolor='#9ABFE8', gridwidth=1,
        zeroline=True, zerolinecolor='#174D95', zerolinewidth=2.5,
        showline=True, linecolor='#9EC5F1',
        tickfont=dict(family='Arial', size=17, color='#122D54'),
        tickformat='~f', ticks='outside', ticklen=5,
        tickcolor='#174D95', automargin=True,
        constrain='domain'
    )
    px = passo if escala_real else max(1, passo_grade(xmax-xmin))
    py = passo if escala_real else max(1, passo_grade(ymax-ymin))
    # Quando a escala é igual, expande a janela em vez de criar uma faixa fina.
    grade.pop('constrain', None)
    fig.update_xaxes(range=[xmin, xmax], dtick=px,
                     minor=dict(dtick=px/5, showgrid=True, gridcolor='#DFECFA', gridwidth=0.5), **grade)
    fig.update_yaxes(range=[ymin, ymax], dtick=py,
                     minor=dict(dtick=py/5, showgrid=True, gridcolor='#DFECFA', gridwidth=0.5), **grade)
    if escala_real:
        fig.update_yaxes(scaleanchor='x', scaleratio=1)
    return fig


def racional(v):
    return Fraction(str(v))


def exato(v):
    """Decimal finito sem zeros finais; fração se a expansão for infinita."""
    v = Fraction(v)
    d = v.denominator
    p = q = 0
    while d % 2 == 0:
        d //= 2
        p += 1
    while d % 5 == 0:
        d //= 5
        q += 1
    if d != 1:
        return frac_latex(v)
    k = max(p, q)
    n = abs(v.numerator) * 2**(k-p) * 5**(k-q)
    s = str(n).zfill(k+1)
    if k:
        s = (s[:-k] + '{,}' + s[-k:]).rstrip('0')
        if s.endswith('{,}'):
            s = s[:-3]
    return ('-' if v < 0 else '') + s


def fracao(numerador, denominador):
    return rf'\frac{{{numerador}}}{{{denominador}}}'


def raiz_racional(v):
    n, d = math.isqrt(v.numerator), math.isqrt(v.denominator)
    return Fraction(n, d) if n*n == v.numerator and d*d == v.denominator else None


def identificar_coeficientes(a, b, c):
    st.markdown('### Identificando os coeficientes')
    st.write('Compare a função do exercício com a forma geral. Cada letra representa um número, incluindo o seu sinal.')
    st.latex(r'f(x)=\underbrace{ax^2}_{\text{2º grau}}+\underbrace{bx}_{\text{1º grau}}+\underbrace{c}_{\text{constante}}')
    itens = [('a', a, 'x^2', 'É o número que multiplica x². Seu sinal define a concavidade; seu módulo controla a abertura.', 'blue'),
             ('b', b, 'x', 'É o número que multiplica x. Junto com a, determina a posição horizontal do vértice.', 'orange'),
             ('c', c, '', 'É o termo independente. Indica onde a parábola encontra o eixo y: f(0) = c.', 'green')]
    for coluna, (letra, valor, potencia, descricao, cor) in zip(st.columns(3), itens):
        with coluna:
            with st.container(border=True):
                st.markdown(f'**:{cor}[Coeficiente {letra}]**')
                st.latex(rf'\boxed{{{letra}={exato(racional(valor))}}}')
                termo = '(' + exato(racional(valor)) + ')' + potencia if potencia else exato(racional(valor))
                st.latex(termo)
                st.write(descricao)
    if a in (-1, 1) or b in (-1, 1):
        st.caption('Quando x² ou x aparece sem número escrito, o coeficiente é 1; se aparece apenas o sinal de menos, é −1.')
    if b == 0 or c == 0:
        ausentes = ['bx' for _ in [0] if b == 0] + ['c' for _ in [0] if c == 0]
        st.info('Termo ausente: ' + ' e '.join(ausentes) + '. Seu coeficiente é zero, não 1.')
    st.write('Identificamos os coeficientes pelo grau do termo, não pela ordem em que aparecem no exercício. O sinal pertence ao número.')
    st.info('É uma função do segundo grau porque o maior expoente de x é 2. Como a é diferente de zero, seu gráfico é uma parábola. Se a = 0, o termo x² desaparece.')


def passo(texto, formula):
    st.markdown('**' + texto + '**')
    st.latex(formula)


def soma_escrita(u, v):
    return exato(u) + ('+' if v >= 0 else '-') + exato(abs(v))


def resolucao_visual(a, b, c, delta, xv, yv, raizes, fig):
    af, bf, cf = map(racional, (a, b, c))
    b2, ac, quatroac = bf**2, af*cf, 4*af*cf
    df = b2-quatroac
    vx, vy = -bf/(2*af), -df/(4*af)
    A, B, C, D = map(exato, (af, bf, cf, df))
    st.header('Aprendendo passo a passo')
    st.latex(latex_funcao(a,b,c))
    identificar_coeficientes(a,b,c)
    with st.container(border=True):
        st.markdown('### :blue[01 — Concavidade]')
        passo('1. Localize o coeficiente de x².', rf'a={A}')
        passo('2. Compare com zero.', rf'a={A}'+('>0' if af>0 else '<0'))
        st.write('3. Como a é positivo, a parábola abre para cima e tem um ponto mais baixo.' if af>0 else '3. Como a é negativo, a parábola abre para baixo e tem um ponto mais alto.')
        for coluna, sentido in zip(st.columns(2), (1,-1)):
            with coluna:
                atual = (af>0)==(sentido>0)
                st.markdown('**Para cima — a positivo**' if sentido>0 else '**Para baixo — a negativo**')
                st.plotly_chart(grafico_concavidade(sentido, atual), theme=None, key=f'aula_concavidade_{sentido}', config={'displayModeBar':False})
                if atual:
                    st.success('É o caso da sua função.')
        st.caption('Esses dois desenhos são exemplos de comparação; o gráfico principal representa a função digitada.')

    with st.container(border=True):
        st.markdown('### :blue[02 — Discriminante (delta)]')
        st.write('Delta nos ajuda a descobrir quantas raízes reais existem. Primeiro resolvemos a potência e as multiplicações; só depois fazemos a subtração.')
        passo('1. Escrevemos a fórmula.', r'\Delta=b^2-4ac')
        passo('2. Substituímos a, b e c. Usamos parênteses para preservar os sinais.', rf'\Delta=({B})^2-4\cdot({A})\cdot({C})')
        passo('3. Elevamos b ao quadrado: multiplicamos b por ele mesmo.', rf'({B})^2=({B})\cdot({B})={exato(b2)}')
        passo('4. Multiplicamos a por c e, depois, por 4.', rf'({A})\cdot({C})={exato(ac)}\qquad 4\cdot({exato(ac)})={exato(quatroac)}')
        passo('5. Substituímos os resultados na expressão.', rf'\Delta={exato(b2)}-({exato(quatroac)})')
        passo('6. Resolvemos os sinais e calculamos.', rf'\Delta={soma_escrita(b2,-quatroac)}={D}')
        st.latex(rf'\boxed{{\Delta={D}}}')
        if df > 0:
            st.success('Delta positivo: duas raízes reais distintas.')
        elif df == 0:
            st.info('Delta igual a zero: uma raiz real distinta (raiz dupla).')
        else:
            st.warning('Delta negativo: não existem raízes reais.')

    with st.container(border=True):
        st.markdown('### :green[03 — Zeros da função (Bhaskara)]')
        st.write('Zero da função é um valor de x que faz f(x) valer 0. Por isso, igualamos a função a zero.')
        st.latex(latex_funcao(a,b,c).split('=',1)[1]+'=0')
        passo('1. Escrevemos a fórmula de Bhaskara.',r'x=\frac{-b\pm\sqrt{\Delta}}{2a}')
        if df < 0:
            st.latex(rf'\sqrt{{\Delta}}=\sqrt{{{D}}}')
            st.warning('Não existe raiz quadrada real de número negativo. Encerramos o cálculo dos zeros: o gráfico não corta nem toca o eixo x.')
        else:
            passo('2. Substituímos b, delta e a.', 'x='+fracao(rf'-({B})\pm\sqrt{{{D}}}',rf'2\cdot({A})'))
            passo('3. Resolvemos o oposto de b e o denominador.',rf'-b=-({B})={exato(-bf)}\qquad 2a=2\cdot({A})={exato(2*af)}')
            sr = raiz_racional(df)
            radical = exato(sr) if sr is not None else rf'\sqrt{{{D}}}'
            if sr is not None:
                passo('4. Calculamos a raiz quadrada de delta.',rf'\sqrt{{{D}}}={radical}')
            else:
                passo('4. A raiz quadrada não é racional. Mantemos a expressão exata.',rf'\sqrt{{{D}}}'+resultado_latex(math.sqrt(delta)))
            if df == 0:
                st.write('Somar zero ou subtrair zero produz o mesmo resultado.')
                passo('5. Resolvemos a divisão.', 'x='+fracao(exato(-bf),exato(2*af))+'='+exato(vx))
                st.latex(rf'\boxed{{x={exato(vx)}}}')
            else:
                passo('5. Separamos as duas possibilidades do sinal ±.', 'x='+fracao(exato(-bf)+r'\pm'+radical,exato(2*af)))
                st.caption('As raízes são organizadas da menor para a maior. Se a for negativo, a ordem dos sinais se inverte.')
                sinais = [-1,1] if af > 0 else [1,-1]
                for i,(coluna,sinal) in enumerate(zip(st.columns(2),sinais),1):
                    with coluna:
                        with st.container(border=True):
                            st.markdown(f'#### Raiz {i} — sinal '+('menos' if sinal < 0 else 'mais'))
                            nome=rf'x_{i}'
                            formula=fracao(exato(-bf)+('+' if sinal>0 else '-')+radical,exato(2*af))
                            st.latex(nome+'='+formula)
                            if sr is not None:
                                numerador=-bf+sinal*sr
                                r=numerador/(2*af)
                                passo('Resolvemos o numerador.', soma_escrita(-bf,sinal*sr)+'='+exato(numerador))
                                passo('Dividimos pelo denominador.',nome+'='+fracao(exato(numerador),exato(2*af)))
                                st.latex(rf'\boxed{{{nome}={exato(r)}}}')
                                if r.denominator != 1 and '{,}' not in exato(r):
                                    st.latex(nome+resultado_latex(raizes[i-1]))
                            else:
                                st.write('Conservamos a forma exata acima e aproximamos somente o resultado final.')
                                st.latex(r'\boxed{'+nome+resultado_latex(raizes[i-1])+'}')
            st.caption('Os zeros são as abscissas dos pontos onde a parábola encontra o eixo x.')

    with st.container(border=True):
        st.markdown('### :orange[04 — Vértice da parábola]')
        st.write('O vértice é um ponto com duas coordenadas: x indica a posição horizontal, e y, a altura. É o ponto mais baixo ou mais alto do gráfico.')
        vxcol, vycol = st.columns(2)
        for col, nome, descr, formula, bruto, numerador, den, resultado in [
            (vxcol,'x_v','Abscissa',r'x_v=\frac{-b}{2a}',fracao('-('+B+')','2\\cdot('+A+')'),-bf,2*af,vx),
            (vycol,'y_v','Ordenada',r'y_v=\frac{-\Delta}{4a}',fracao('-('+D+')','4\\cdot('+A+')'),-df,4*af,vy)]:
            with col:
                with st.container(border=True):
                    st.markdown('#### '+descr+' do vértice')
                    passo('1. Fórmula.',formula)
                    passo('2. Substituição.',nome+'='+bruto)
                    passo('3. Resolvemos o sinal e a multiplicação.',nome+'='+fracao(exato(numerador),exato(den)))
                    passo('4. Fazemos a divisão.',r'\boxed{'+nome+'='+exato(resultado)+'}')
                    if resultado.denominator != 1 and '{,}' not in exato(resultado):
                        st.latex(nome+resultado_latex(float(resultado)))
        st.latex(rf'\boxed{{V=\left({exato(vx)};\,{exato(vy)}\right)}}')
        with st.container(border=True):
            st.markdown('#### Conferindo a ordenada por substituição em f(x)')
            t1,t2=af*vx**2,bf*vx
            st.latex(rf'f({exato(vx)})=({A})\cdot({exato(vx)})^2+({B})\cdot({exato(vx)})+({C})')
            st.latex(rf'f({exato(vx)})=({A})\cdot({exato(vx**2)})+({B})\cdot({exato(vx)})+({C})')
            st.latex(rf'f({exato(vx)})=({exato(t1)})+({exato(t2)})+({C})')
            st.latex(rf'f({exato(vx)})={soma_escrita(t1+t2,cf)}')
            st.latex(rf'f({exato(vx)})={exato(vy)}=y_v')
        mini = go.Figure(fig)
        mini.update_layout(height=400,showlegend=False,margin=dict(l=50,r=30,t=15,b=40))
        st.plotly_chart(mini,theme=None,key='q_grafico_resolucao')
        st.info('Parábola para cima: o vértice é o ponto de mínimo.' if af>0 else 'Parábola para baixo: o vértice é o ponto de máximo.')

    with st.container(border=True):
        st.markdown('### :orange[05 — Valor máximo e valor mínimo]')
        passo('1. Recupere o sinal de a.', rf'a={A}'+('>0' if af>0 else '<0'))
        st.write('2. Se a parábola abre para cima, ela desce até o vértice e volta a subir. Se abre para baixo, sobe até o vértice e volta a descer.')
        passo('3. Localize o ponto extremo (vértice).', rf'V=\left({exato(vx)};{exato(vy)}\right)')
        passo('4. O valor extremo é a coordenada y, não a coordenada x.', rf'f_{{{"min" if af>0 else "max"}}}=f\left({exato(vx)}\right)=y_v={exato(vy)}')
        st.success('Existe mínimo global e não existe máximo, pois os ramos sobem sem limite.' if af>0 else 'Existe máximo global e não existe mínimo, pois os ramos descem sem limite.')

    with st.container(border=True):
        st.markdown('### :blue[06 — Eixo de simetria]')
        st.write('1. O eixo é uma reta vertical que passa pelo vértice e divide a parábola em duas metades espelhadas.')
        passo('2. Pegue a coordenada horizontal do vértice.', rf'x_v={exato(vx)}')
        passo('3. Escreva a equação da reta.', rf'\boxed{{x={exato(vx)}}}')
        st.write('4. Podemos conferir escolhendo dois valores de x à mesma distância do eixo. As alturas precisam ser iguais.')
        l,r=vx-1,vx+1
        st.latex(rf'x_E={exato(vx)}-1={exato(l)}\qquad x_D={exato(vx)}+1={exato(r)}')
        st.latex(rf'f({exato(l)})=f({exato(r)})={exato(af+vy)}')
        st.caption('A linha vertical tracejada no gráfico indica esse eixo.')

    with st.container(border=True):
        st.markdown('### :blue[07 — Domínio]')
        st.write('1. Domínio é o conjunto de valores que podemos colocar no lugar de x.')
        st.latex(latex_funcao(a,b,c))
        st.write('2. Nesta expressão, fazemos potências inteiras não negativas, multiplicações e somas. Podemos executar essas operações com qualquer número real. Não há divisão por x nem raiz quadrada de uma expressão em x.')
        passo('3. Por isso, não há restrições neste estudo.', r'\boxed{D(f)=\mathbb{R}}')
        st.caption('ℝ representa todos os números reais, incluindo negativos, zero, positivos, frações e irracionais.')

    with st.container(border=True):
        st.markdown('### :blue[08 — Conjunto imagem]')
        st.write('1. Diferentemente do domínio, a imagem é o conjunto das alturas y que a função realmente atinge.')
        passo('2. Recupere a altura do vértice.', rf'y_v={exato(vy)}')
        passo('3. Observe a forma de vértice da função.', 'f(x)='+exato(af)+r'(x-('+exato(vx)+r'))^2'+('+' if vy>=0 else '-')+exato(abs(vy)))
        st.write('4. Um quadrado nunca é negativo. Como a é positivo, a parcela com o quadrado também nunca é negativa. Portanto f(x) nunca fica abaixo de yᵥ.' if af>0 else '4. Um quadrado nunca é negativo. Como a é negativo, multiplicá-lo pelo quadrado produz um valor menor ou igual a zero. Portanto f(x) nunca fica acima de yᵥ.')
        passo('5. Escreva a desigualdade.', (r'y\geq ' if af>0 else r'y\leq ')+exato(vy))
        passo('6. Escreva o intervalo da imagem.', r'\boxed{\operatorname{Im}(f)='+ (rf'[{exato(vy)}; +\infty)' if af>0 else rf'(-\infty; {exato(vy)}]')+'}')
        st.write('O colchete inclui a altura do vértice, que é atingida. O parêntese no infinito indica que o infinito não é um número que a função atinge.')
        st.plotly_chart(grafico_imagem(af,vy),theme=None,key='aula_imagem',config={'displayModeBar':False})

    with st.container(border=True):
        st.markdown('### :green[09 — Estudo do sinal da função]')
        st.write('1. Estudar o sinal é descobrir para quais valores de x a função tem altura positiva, nula ou negativa. Não confunda o sinal de x com o sinal de f(x).')
        st.write('2. Recupere os zeros, que são os pontos de encontro com o eixo x.')
        limites=limites_exatos(a,b,c)
        if df>0:
            st.latex(rf'x_1={limites[0]}' if limites[0]!='x_1' else r'x_1'+resultado_latex(raizes[0]))
            st.latex(rf'x_2={limites[1]}' if limites[1]!='x_2' else r'x_2'+resultado_latex(raizes[1]))
            st.write('3. Os dois zeros dividem a reta em três intervalos. Fora das raízes o sinal é o mesmo de a; entre as raízes é o contrário. Podemos conferir escolhendo um valor de x em cada intervalo.')
            amostras=[('Antes da primeira raiz',Fraction(math.floor(raizes[0])-1)),('Entre as raízes',vx),('Depois da segunda raiz',Fraction(math.ceil(raizes[1])+1))]
        elif df==0:
            st.latex('x_0='+limites[0])
            st.write('3. A raiz dupla divide a reta em dois intervalos. A parábola toca o eixo x, mas não o atravessa. Podemos verificar um ponto de cada lado.')
            amostras=[('Antes da raiz',vx-1),('Depois da raiz',vx+1)]
        else:
            st.write('3. Não há zeros reais. Como a parábola é contínua e nunca encontra o eixo x, o sinal de f(x) é constante. Vamos conferir no vértice.')
            amostras=[('Em toda a reta (exemplo no vértice)',vx)]
        for titulo, t in amostras:
            with st.container(border=True):
                st.markdown('**'+titulo+'**')
                conta_ponto(af,bf,cf,t)
        st.write('4. Complete o quadro: + indica acima do eixo x, − indica abaixo e 0 indica sobre o eixo.')
        st.plotly_chart(grafico_sinal(a,delta,raizes),theme=None,key='q_sinal_resolucao',config={'displayModeBar':False})
        st.write('5. Escreva os conjuntos-solução dos três sinais. O símbolo ∅ significa que não existe valor de x que satisfaça a condição.')
        for nome, conjunto in zip(['f(x)>0','f(x)=0','f(x)<0'],intervalos_sinal(a,delta,limites)):
            st.latex(nome+r'\quad\Longleftrightarrow\quad x\in '+conjunto)
        st.caption('Quando os limites são irracionais, x₁ e x₂ representam os valores exatos calculados por Bhaskara; os números no quadro são aproximações.')

    with st.container(border=True):
        st.markdown('### :blue[10 — Crescimento e decrescimento]')
        st.write('1. Leia o gráfico sempre da esquerda para a direita, isto é, no sentido em que x aumenta. Crescer significa que y aumenta; decrescer significa que y diminui.')
        passo('2. O vértice separa os dois trechos.',rf'x_v={exato(vx)}')
        st.write('3. Antes do vértice a função desce e depois sobe.' if af>0 else '3. Antes do vértice a função sobe e depois desce.')
        st.plotly_chart(grafico_variacao(af, vx),theme=None,key='aula_variacao',config={'displayModeBar':False})
        passo('4. Intervalo crescente.', rf'[{exato(vx)}; +\infty)' if af>0 else rf'(-\infty; {exato(vx)}]')
        passo('5. Intervalo decrescente.', rf'(-\infty; {exato(vx)}]' if af>0 else rf'[{exato(vx)}; +\infty)')
        st.caption('Incluímos o vértice nas extremidades dos intervalos de monotonicidade; a função muda de comportamento nesse ponto.')
    st.caption('Os resultados exatos são preservados, com frações quando necessário. O símbolo ≈ indica aproximação. Inteiros são exibidos sem casas decimais.')


def frac_latex(v):
    """Representação exata de um racional, sem zeros supérfluos."""
    if v.denominator == 1:
        return str(v.numerator)
    sinal = '-' if v < 0 else ''
    return sinal + rf'\frac{{{abs(v.numerator)}}}{{{v.denominator}}}'


def dados_sinal(a, delta):
    """Sinais dos intervalos abertos e dos pontos, da esquerda para a direita."""
    s = '+' if a > 0 else '−'
    op = '−' if a > 0 else '+'
    if delta > 0:
        return [s, '0', op, '0', s]
    if delta == 0:
        return [s, '0', s]
    return [s]


def intervalos_sinal(a, delta, limites):
    """Conjuntos de solução para f(x)>0, =0 e <0 em LaTeX."""
    if delta > 0:
        r1, r2 = limites
        fora = rf'(-\infty,{r1})\cup({r2},+\infty)'
        dentro = rf'({r1},{r2})'
        zeros = rf'\left\{{{r1},{r2}\right\}}'
        return (fora, zeros, dentro) if a > 0 else (dentro, zeros, fora)
    if delta == 0:
        r = limites[0]
        fora = rf'(-\infty,{r})\cup({r},+\infty)'
        zeros = rf'\left\{{{r}\right\}}'
        return (fora, zeros, r'\varnothing') if a > 0 else (r'\varnothing', zeros, fora)
    return (r'\mathbb{R}', r'\varnothing', r'\varnothing') if a > 0 else (r'\varnothing', r'\varnothing', r'\mathbb{R}')


def limites_exatos(a, b, c):
    """Raízes racionais exatas, ou símbolos x_1 e x_2 para raízes irracionais."""
    af, bf, cf = (Fraction(str(v)) for v in (a,b,c))
    d = bf*bf-4*af*cf
    if d < 0:
        return []
    if d == 0:
        return [frac_latex(-bf/(2*af))]
    n, den = math.isqrt(d.numerator), math.isqrt(d.denominator)
    if n*n == d.numerator and den*den == d.denominator:
        s = Fraction(n, den)
        return [frac_latex(v) for v in sorted([(-bf-s)/(2*af),(-bf+s)/(2*af)])]
    return ['x_1','x_2']


def grafico_sinal(a, delta, raizes):
    sinais = dados_sinal(a, delta)
    n = len(sinais)
    fig = go.Figure()
    pos = list(range(n))
    for i, sinal in enumerate(sinais):
        cor = {'+':'#15803D','−':'#B91C1C','0':'#875400'}[sinal]
        fundo = {'+':'#DCFCE7','−':'#FEE2E2','0':'#FEF3C7'}[sinal]
        fig.add_shape(type='rect', x0=i-.48,x1=i+.48,y0=.27,y1=.83,
                      fillcolor=fundo,line=dict(color=cor,width=1))
        fig.add_annotation(x=i,y=.55,text=f'<b>{sinal}</b>',showarrow=False,
                           font=dict(size=28,color=cor))
        if sinal == '0':
            j = (i-1)//2
            r = raizes[j]
            rel = '=' if float(fmt(r)) == r else '≈'
            nome = 'x₀' if delta == 0 else ('x₁' if j == 0 else 'x₂')
            fig.add_annotation(x=i,y=.1,text=f'<b>{nome} {rel} {fmt(r)}</b>',
                               showarrow=False,font=dict(size=15,color='#122D54'))
    fig.add_annotation(x=-.43,y=.1,text='−∞',showarrow=False,xanchor='left',font=dict(size=16,color='#122D54'))
    fig.add_annotation(x=n-.57,y=.1,text='+∞',showarrow=False,xanchor='right',font=dict(size=16,color='#122D54'))
    fig.update_layout(height=190,template='plotly_white',paper_bgcolor='white',plot_bgcolor='white',
                      margin=dict(l=12,r=12,t=15,b=10),showlegend=False)
    fig.update_xaxes(range=[-.55,n-.45],visible=False,fixedrange=True)
    fig.update_yaxes(range=[0,1],visible=False,fixedrange=True)
    return fig


def grafico_concavidade(sentido, selecionado):
    """Exemplo fixo para comparar o sinal de a, sem influência de b e c."""
    cor = AZUL if sentido > 0 else '#B45309'
    x = np.linspace(-2.4, 2.4, 401)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=sentido*x**2, mode='lines',
        line=dict(color=cor, width=4), hoverinfo='skip', showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers', showlegend=False,
        marker=dict(color='#15803D', size=12, line=dict(color='white', width=1)),
        hovertemplate='Vértice (0; 0)<extra></extra>'
    ))
    # As setas acompanham a direção das duas extremidades da parábola.
    for lado in [-1, 1]:
        fig.add_annotation(x=lado*2.23, y=sentido*2.23**2,
                           ax=lado*1.95, ay=sentido*1.95**2,
                           axref='x', ayref='y', showarrow=True, text='',
                           arrowhead=3, arrowsize=1.3, arrowwidth=2.5, arrowcolor=cor)
    fig.add_annotation(x=0, y=0, text='<b>Mínimo</b>' if sentido>0 else '<b>Máximo</b>',
                       showarrow=False, yshift=-23 if sentido>0 else 23,
                       font=dict(size=14, color='#166534'), bgcolor='white')
    fig.update_layout(
        template='plotly_white', paper_bgcolor='white', plot_bgcolor='white',
        height=360, margin=dict(l=42,r=35,t=18,b=42),
        showlegend=False, font=dict(family='Arial', size=14, color='#173B70')
    )
    grade=dict(showgrid=True, gridcolor='#A5CAEF', gridwidth=1, dtick=1,
               zeroline=True, zerolinewidth=2, zerolinecolor='#174D95',
               tickfont=dict(size=14,color='#122D54'), tickformat='~f',
               fixedrange=True, minor=dict(dtick=.2,showgrid=True,gridcolor='#DFECFA',gridwidth=.5))
    fig.update_xaxes(range=[-3,3], title_text='x', constrain='domain', **grade)
    fig.update_yaxes(range=[-1.5,6.5] if sentido>0 else [-6.5,1.5],
                     title_text='y', scaleanchor='x', scaleratio=1, constrain='domain', **grade)
    fig.add_shape(type='rect',xref='paper',yref='paper',x0=0,x1=1,y0=0,y1=1,
                  line=dict(color='#15803D' if selecionado else '#A5CAEF',width=3 if selecionado else 1))
    return fig


def painel_concavidade(a, b, c):
    af,bf,cf = map(racional, (a,b,c))
    vx = -bf/(2*af)
    vy = -(bf**2-4*af*cf)/(4*af)
    st.header('Estudo visual da concavidade')
    st.write('Observe apenas o sinal do coeficiente a, que multiplica x². '
             'Os coeficientes b e c não mudam o sentido da abertura.')
    st.latex(r'a='+num(a)+('>0' if a>0 else '<0'))
    esquerda, direita = st.columns(2)
    for coluna, sentido in [(esquerda, 1), (direita, -1)]:
        atual = (a>0) == (sentido>0)
        with coluna:
            with st.container(border=True):
                st.markdown('### :blue[Concavidade para cima]' if sentido>0 else '### :orange[Concavidade para baixo]')
                st.latex(r'a>0' if sentido>0 else r'a<0')
                st.latex(r'f(x)=x^2' if sentido>0 else r'f(x)=-x^2')
                st.plotly_chart(grafico_concavidade(sentido, atual), theme=None,
                                key=f'q_concavidade_{sentido}', config={'displayModeBar':False})
                st.write('A parábola possui um ponto mais baixo (mínimo).' if sentido>0 else
                         'A parábola possui um ponto mais alto (máximo).')
                if atual:
                    st.success('Este é o sentido da abertura da função digitada.')
                else:
                    st.caption('Este é o outro caso possível.')
    st.caption('Os dois gráficos acima são exemplos de comparação. O gráfico principal mostra a função que você digitou.')
    if a>0:
        st.info('Na sua função, a concavidade é para cima porque a é positivo. O vértice é o ponto de mínimo. Não existe máximo.')
    else:
        st.info('Na sua função, a concavidade é para baixo porque a é negativo. O vértice é o ponto de máximo. Não existe mínimo.')
    st.latex(rf'V=\left({exato(vx)};{exato(vy)}\right)')


def estudo_completo(a,b,c,delta,xv,yv,raizes):
    af,bf,cf = (Fraction(str(v)) for v in (a,b,c))
    df = bf*bf-4*af*cf
    vx,vy = -bf/(2*af), -df/(4*af)
    vx_l,vy_l = frac_latex(vx),frac_latex(vy)
    limites = limites_exatos(a,b,c)
    st.header('Estudo completo da função quadrática')
    st.latex(latex_funcao(a,b,c))
    st.latex(rf'a={exato(af)}\qquad b={exato(bf)}\qquad c={exato(cf)}')
    st.latex(rf'\Delta={exato(df)}')
    with st.container(border=True):
        esquerda,direita = st.columns(2)
        with esquerda:
            st.markdown('### :blue[01 — Concavidade]')
            st.latex(rf'a={num(a)}'+('>0' if a>0 else '<0'))
            st.write('Abertura para cima (∪).' if a>0 else 'Abertura para baixo (∩).')
            st.markdown('### :green[02 — Zeros da função]')
            st.latex(r'f(x)=0')
            if delta < 0:
                st.write('Não possui zeros reais: a parábola não intercepta o eixo x.')
            elif delta == 0:
                st.latex(r'x_0='+limites[0])
                st.write('Uma raiz dupla: a parábola toca o eixo x.')
            else:
                for i,(r,l) in enumerate(zip(raizes,limites),1):
                    if l.startswith('x_'):
                        sinal = '-' if (i==1)==(a>0) else '+'
                        forma = rf'\frac{{-({frac_latex(bf)}){sinal}\sqrt{{{frac_latex(df)}}}}}{{2\cdot({frac_latex(af)})}}'
                        st.latex(rf'x_{i}={forma}'+resultado_latex(r))
                    else:
                        st.latex(rf'x_{i}={l}')
                st.write('Duas raízes distintas: a parábola cruza o eixo x em dois pontos.')
        with direita:
            st.markdown('### :orange[03 — Vértice da parábola]')
            st.latex(r'V=(x_v,y_v)')
            st.latex(rf'V=\left({vx_l};{vy_l}\right)')
            st.latex(rf'\text{{Eixo de simetria: }} x={vx_l}')
            st.markdown('### :orange[04 — Máximo e mínimo]')
            if a>0:
                st.latex(rf'f_{{\min}}=f({vx_l})={vy_l}')
                st.write('Possui mínimo global e não possui máximo.')
            else:
                st.latex(rf'f_{{\max}}=f({vx_l})={vy_l}')
                st.write('Possui máximo global e não possui mínimo.')
    with st.container(border=True):
        st.markdown('### :blue[05 — Domínio e imagem]')
        c1,c2 = st.columns(2)
        with c1:
            st.write('Domínio: todos os números reais.')
            st.latex(r'D(f)=\mathbb{R}')
        with c2:
            st.write('Imagem: todos os valores que a função pode assumir.')
            if a>0:
                st.latex(rf'\operatorname{{Im}}(f)=[{vy_l},+\infty)')
                st.latex(rf'y\geq {vy_l}')
            else:
                st.latex(rf'\operatorname{{Im}}(f)=(-\infty,{vy_l}]')
                st.latex(rf'y\leq {vy_l}')
    with st.container(border=True):
        st.markdown('### :green[06 — Estudo do sinal da função]')
        st.write('O sinal depende da posição da parábola em relação ao eixo x: acima é positivo, abaixo é negativo e sobre o eixo é zero.')
        st.plotly_chart(grafico_sinal(a,delta,raizes),theme=None,key='q_sinal',config={'displayModeBar':False})
        st.caption('Quadro esquemático: os intervalos não estão em escala. Os limites exatos aparecem abaixo ou na seção de zeros.')
        positivo,zero,negativo = intervalos_sinal(a,delta,limites)
        for titulo,formula,cor in [('f(x)>0',positivo,'green'),('f(x)=0',zero,'orange'),('f(x)<0',negativo,'red')]:
            st.markdown(f'**:{cor}[{titulo}]**')
            st.latex(r'x\in '+formula)
        if delta > 0:
            st.write('A função tem o mesmo sinal de a fora das raízes e o sinal oposto entre elas.')
        elif delta == 0:
            st.write('A função mantém o sinal de a dos dois lados da raiz dupla; não há troca de sinal.')
        else:
            st.write('Como não há zeros reais, a função mantém o sinal de a em todo o domínio.')
    with st.container(border=True):
        st.markdown('### :blue[07 — Crescimento e decrescimento]')
        antes, depois = rf'(-\infty,{vx_l}]',rf'[{vx_l},+\infty)'
        esquerda,direita = st.columns(2)
        with esquerda:
            st.write('Decrescente' if a>0 else 'Crescente')
            st.latex(antes)
        with direita:
            st.write('Crescente' if a>0 else 'Decrescente')
            st.latex(depois)



def conta_ponto(a,b,c,x):
    A,B,C,X=map(exato,(a,b,c,x))
    p,q=a*x*x,b*x
    v=p+q+c
    st.latex(rf'f({X})=({A})\cdot({X})^2+({B})\cdot({X})+({C})')
    st.latex(rf'f({X})=({A})\cdot({exato(x*x)})+({B})\cdot({X})+({C})')
    st.latex(rf'f({X})=({exato(p)})+({exato(q)})+({C})')
    st.latex(rf'f({X})={soma_escrita(p+q,c)}={exato(v)}')
    st.latex(rf'f({X})'+('>0' if v>0 else '<0' if v<0 else '=0'))
    return v


def grafico_imagem(a,vy):
    sentido=1 if a>0 else -1
    fig=go.Figure()
    fig.add_shape(type='line',x0=0,x1=0,y0=-3,y1=3,line=dict(color='#9ABFE8',width=2))
    fig.add_annotation(x=0,y=2.6*sentido,ax=0,ay=0,axref='x',ayref='y',text='',showarrow=True,arrowhead=3,arrowwidth=8,arrowcolor=VERDE)
    fig.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(size=17,color=VERDE,line=dict(color='white',width=1)),hoverinfo='skip'))
    fig.add_annotation(x=0,y=0,text='<b>yᵥ '+('= ' if Fraction(fmt(float(vy)))==vy else '≈ ')+fmt(float(vy))+'</b>',showarrow=False,xshift=18,xanchor='left',font=dict(size=16,color='#122D54'))
    fig.add_annotation(x=0,y=2.6*sentido,text='+∞' if a>0 else '−∞',xshift=18,xanchor='left',showarrow=False,font=dict(size=17,color=VERDE))
    fig.update_layout(height=255,template='plotly_white',paper_bgcolor='white',plot_bgcolor='white',showlegend=False,margin=dict(l=15,r=15,t=12,b=12))
    fig.update_xaxes(visible=False,range=[-1,1],fixedrange=True)
    fig.update_yaxes(visible=False,range=[-3.2,3.2],fixedrange=True)
    return fig


def grafico_variacao(a,vx):
    s=1 if a>0 else -1
    fig=go.Figure()
    for lado,cor in [(-1,'#B91C1C' if a>0 else VERDE),(1,VERDE if a>0 else '#B91C1C')]:
        xx=np.linspace(-2,0,100) if lado<0 else np.linspace(0,2,100)
        fig.add_trace(go.Scatter(x=xx,y=s*xx**2,mode='lines',line=dict(color=cor,width=5),hoverinfo='skip',showlegend=False))
        p,q=(-1.6,-.9) if lado<0 else (.9,1.6)
        fig.add_annotation(x=q,y=s*q*q,ax=p,ay=s*p*p,axref='x',ayref='y',text='',showarrow=True,arrowhead=3,arrowwidth=2,arrowcolor=cor)
        fig.add_annotation(x=lado*1.15,y=s*3.45,text='<b>'+('Crescente' if cor==VERDE else 'Decrescente')+'</b>',showarrow=False,font=dict(color=cor,size=15))
    fig.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(size=13,color=LARANJA),hoverinfo='skip',showlegend=False))
    fig.add_vline(x=0,line_dash='dash',line_color=LARANJA)
    fig.add_annotation(x=0,y=0,text='xᵥ ≈ '+fmt(float(vx)) if Fraction(fmt(float(vx)))!=vx else 'xᵥ = '+fmt(float(vx)),showarrow=False,yshift=-22 if a>0 else 22,font=dict(size=15,color='#875400'))
    fig.update_layout(height=280,template='plotly_white',paper_bgcolor='white',plot_bgcolor='white',margin=dict(l=15,r=15,t=12,b=15),showlegend=False)
    fig.update_xaxes(visible=False,range=[-2.45,2.45],fixedrange=True)
    fig.update_yaxes(visible=False,range=[-1,4.8] if a>0 else [-4.8,1],fixedrange=True)
    return fig


def oficina_grafico(a,b,c,fig,raizes):
    af,bf,cf=map(racional,(a,b,c))
    vx=-bf/(2*af)
    st.header('Construindo o gráfico à mão')
    st.write('1. Escolha valores de x. Por padrão, usamos cinco inteiros próximos do vértice. Você também pode digitar seus próprios valores.')
    centro=math.floor(vx)
    pontos=[Fraction(x) for x in range(centro-2,centro+3)]
    escolha=st.radio('Valores de x', ['Automáticos', 'Personalizados'], horizontal=True, key='q_pontos_modo')
    if escolha == 'Personalizados':
        entrada=st.text_input('Separe os valores por ponto e vírgula (por exemplo: -2; -1; 0; 1; 2)', value='; '.join(str(x) for x in pontos), key='q_pontos_custom')
        try:
            pontos=list(dict.fromkeys(Fraction(item.strip().replace(',', '.')) for item in entrada.split(';') if item.strip()))
            if not 1 <= len(pontos) <= 12 or any(abs(x)>10**11 or x.denominator>10**6 for x in pontos):
                raise ValueError
        except (ValueError, ZeroDivisionError, OverflowError):
            st.warning('Informe de 1 a 12 números válidos, separados por ponto e vírgula.')
            return
    ys=[af*x*x+bf*x+cf for x in pontos]
    st.write('2. Substitua cada x na expressão e faça as contas. Clique em cada item para acompanhar o cálculo.')
    for x in pontos:
        with st.expander('Calculando f('+fmt(float(x))+')'):
            conta_ponto(af,bf,cf,x)
    st.write('3. Organize os resultados em pares ordenados (x; y).')
    st.table({'x': [fmt(float(x)) if x.denominator == 1 else str(x) for x in pontos],
              'f(x)': [str(y) for y in ys],
              'Par ordenado (x; y)': [f'({x}; {y})' for x,y in zip(pontos,ys)]})
    for inicio in range(0,len(pontos),4):
        grupo=list(zip(pontos,ys))[inicio:inicio+4]
        for col,(x,y) in zip(st.columns(len(grupo)),grupo):
            with col:
                st.latex(rf'\left({exato(x)};{exato(y)}\right)')
    st.write('4. Marque também o vértice, os zeros reais (se existirem) e a interseção com o eixo y. Trace a curva, não segmentos de reta entre os pontos.')
    desenho=go.Figure(fig)
    desenho.add_trace(go.Scatter(x=list(map(float,pontos)),y=list(map(float,ys)),mode='markers',name='Pontos calculados',marker=dict(color='#7C3AED',size=10,symbol='diamond',line=dict(color='white',width=1))))
    incluir=st.checkbox('Mostrar a curva completa', value=True, key='q_oficina_curva')
    if not incluir:
        desenho.data=tuple(t for t in desenho.data if t.name=='Pontos calculados')
        desenho.layout.shapes=()
    xx=list(map(float,pontos)); yy=list(map(float,ys))
    xi,xf=desenho.layout.xaxis.range
    yi,yf=desenho.layout.yaxis.range
    desenho.update_xaxes(range=[min(xi,min(xx)),max(xf,max(xx))])
    desenho.update_yaxes(range=[min(yi,min(yy)),max(yf,max(yy))])
    if min(xx)<xi or max(xx)>xf:
        xs=np.linspace(min(xi,min(xx)),max(xf,max(xx)),1800)
        for t in desenho.data:
            if t.name=='Parábola':
                t.x=xs
                t.y=a*xs**2+b*xs+c
                t.customdata=[[fmt(u),fmt(v)] for u,v in zip(t.x,t.y)]
    st.plotly_chart(desenho, theme=None,key='q_grafico_oficina')
    st.caption('Os pontos roxos são os pares calculados; se algum estiver fora da janela inicial, reduza o zoom do gráfico ou desmarque a escala proporcional.')
    st.write('5. Confira a concavidade e a simetria: o desenho precisa concordar com o estudo feito nas outras abas.')


def gerar_treino(tema):
    """Cria problemas com coeficientes inteiros e soluções exatas."""
    temas=['Coeficientes','Reconhecimento','Concavidade','Discriminante','Raízes',
           'Vértice','Máximo e mínimo','Eixo de simetria','Domínio e imagem',
           'Sinal','Crescimento e decrescimento','Pares ordenados']
    if tema=='Todos os conteúdos':
        tema=random.choice(temas)
    a=random.choice([-3,-2,-1,1,2,3])
    h=random.randint(-4,4)
    modo=random.choice(['duas','dupla','nenhuma'])
    d=random.randint(1,3)
    b=-2*a*h
    c=a*h*h + (-a*d*d if modo=='duas' else 0 if modo=='dupla' else a*d*d)
    delta,xv,yv,raizes=calcular(a,b,c)
    x=random.randint(-4,4)
    valor=a*x*x+b*x+c
    af,bf,cf=map(Fraction,(a,b,c))
    vx=Fraction(-b,2*a)
    vy=Fraction(-int(delta),4*a)
    if tema=='Coeficientes':
        letra=random.choice(['a','b','c'])
        resposta={'a':a,'b':b,'c':c}[letra]
        pergunta=f'Qual é o coeficiente {letra}?'
        opcoes=None
        dica='Observe o termo que multiplica x², o termo que multiplica x e o termo independente.'
        formula=rf'{letra}={resposta}'
    elif tema=='Reconhecimento':
        if random.choice([True,False]):
            a=0
        resposta='Sim' if a else 'Não'
        pergunta='A expressão representa uma função quadrática?'
        opcoes=['Sim','Não']
        dica='Uma função do segundo grau precisa ter um termo em x² com coeficiente diferente de zero.'
        formula=rf'a={a}'
    elif tema=='Concavidade':
        resposta='Para cima' if a>0 else 'Para baixo'
        pergunta='Qual é o sentido da concavidade?'
        opcoes=['Para cima','Para baixo']
        dica='Observe apenas o sinal de a.'
        formula=rf'a={a}'+('>0' if a>0 else '<0')
    elif tema=='Discriminante':
        resposta=int(delta)
        pergunta='Calcule o discriminante (delta).'
        opcoes=None
        dica='Primeiro calcule b², depois 4ac; por último, subtraia.'
        formula=rf'\Delta=({b})^2-4\cdot({a})\cdot({c})={resposta}'
    elif tema=='Raízes':
        resposta=len(raizes)
        pergunta='Quantas raízes reais distintas a função possui?'
        opcoes=None
        dica='O sinal de delta indica a quantidade de zeros reais.'
        formula=rf'\Delta={int(delta)}\quad\Rightarrow\quad {resposta}\text{{ raízes reais distintas}}'
    elif tema=='Vértice':
        coord=random.choice(['x','y'])
        resposta=vx if coord=='x' else vy
        pergunta=f'Calcule a coordenada {coord} do vértice.'
        opcoes=None
        dica='Use xᵥ = −b/(2a) e yᵥ = −Δ/(4a).'
        formula=(rf'x_v=\frac{{-({b})}}{{2\cdot({a})}}={exato(vx)}' if coord=='x' else rf'y_v=\frac{{-({int(delta)})}}{{4\cdot({a})}}={exato(vy)}')
    elif tema=='Máximo e mínimo':
        resposta=vy
        pergunta='Qual é o valor máximo ou mínimo da função?'
        opcoes=None
        dica='O extremo é a altura do vértice, e não a coordenada horizontal.'
        formula=rf'y_v={exato(vy)}'
    elif tema=='Eixo de simetria':
        resposta=vx
        pergunta='Complete a equação do eixo de simetria: x = ?'
        opcoes=None
        dica='A reta vertical passa pela coordenada x do vértice.'
        formula=rf'x=x_v={exato(vx)}'
    elif tema=='Domínio e imagem':
        resposta='y maior ou igual ao y do vértice' if a>0 else 'y menor ou igual ao y do vértice'
        pergunta='Qual é a condição que define o conjunto imagem?'
        opcoes=['Todos os reais','y maior ou igual ao y do vértice','y menor ou igual ao y do vértice']
        dica='O domínio é ℝ, mas a imagem começa ou termina na altura do vértice.'
        formula=('y\\geq ' if a>0 else 'y\\leq ')+exato(vy)
    elif tema=='Sinal':
        resposta='Positivo' if valor>0 else 'Negativo' if valor<0 else 'Zero'
        pergunta=f'Qual é o sinal de f({x})?'
        opcoes=['Positivo','Zero','Negativo']
        dica='Substitua x pelo valor dado e observe o resultado, não o sinal de x.'
        formula=rf'f({x})=({a})\cdot({x})^2+({b})\cdot({x})+({c})={valor}'
    elif tema=='Crescimento e decrescimento':
        resposta='Decrescente' if a>0 else 'Crescente'
        pergunta='Antes do vértice, como a função se comporta?'
        opcoes=['Crescente','Decrescente']
        dica='Leia o gráfico da esquerda para a direita, levando em conta a concavidade.'
        formula=rf'x_v={exato(vx)}'
    else:
        resposta=valor
        pergunta=f'Calcule f({x}) para formar o par ordenado.'
        opcoes=None
        dica='Substitua x, calcule a potência e depois as multiplicações e a soma.'
        formula=rf'f({x})=({a})\cdot({x})^2+({b})\cdot({x})+({c})={valor}'
    return dict(tema=tema,a=a,b=b,c=c,pergunta=pergunta,resposta=resposta,
                opcoes=opcoes,dica=dica,formula=formula)


def conferir_treino(pergunta,entrada):
    esperado=pergunta['resposta']
    if pergunta['opcoes'] is not None:
        return entrada==esperado
    try:
        return Fraction(str(entrada).strip().replace(',','.'))==Fraction(esperado)
    except (ValueError,ZeroDivisionError,OverflowError):
        return False


def painel_treino():
    st.header('Treino guiado')
    st.write('Resolva uma questão de cada vez. Use a dica quando precisar e confira a explicação depois de responder.')
    temas=['Todos os conteúdos','Coeficientes','Reconhecimento','Concavidade','Discriminante','Raízes','Vértice','Máximo e mínimo','Eixo de simetria','Domínio e imagem','Sinal','Crescimento e decrescimento','Pares ordenados']
    tema=st.selectbox('Escolha o conteúdo',temas,key='treino_tema')
    estado=st.session_state
    if 'treino_acertos' not in estado:
        estado.treino_acertos=0
        estado.treino_total=0
        estado.treino_id=0
    if 'treino_questao' not in estado or estado.get('treino_anterior')!=tema:
        estado.treino_anterior=tema
        estado.treino_questao=gerar_treino(tema)
        estado.treino_id+=1
        estado.treino_feedback=None
    c1,c2=st.columns(2)
    c1.metric('Acertos',estado.treino_acertos)
    c2.metric('Questões respondidas',estado.treino_total)
    if st.button('Nova questão',key='treino_nova'):
        estado.treino_questao=gerar_treino(tema)
        estado.treino_id+=1
        estado.treino_feedback=None
    q=estado.treino_questao
    chave=str(estado.treino_id)
    with st.container(border=True):
        st.markdown('### '+q['tema'])
        a,b,c=q['a'],q['b'],q['c']
        if a:
            st.latex(latex_funcao(a,b,c))
        elif b:
            st.latex('f(x)='+num(b)+'x'+('+' if c>=0 else '-')+num(abs(c)))
        else:
            st.latex('f(x)='+num(c))
        st.write(q['pergunta'])
        with st.expander('Preciso de uma dica'):
            st.info(q['dica'])
        with st.form('treino_form_'+chave):
            if q['opcoes']:
                entrada=st.radio('Sua resposta',q['opcoes'],index=None,key='treino_op_'+chave)
            else:
                entrada=st.text_input('Sua resposta',key='treino_num_'+chave,placeholder='Digite um número ou uma fração')
            enviado=st.form_submit_button('Conferir resposta',disabled=estado.treino_feedback is not None)
        if enviado and estado.treino_feedback is None:
            if entrada is None or not str(entrada).strip():
                st.warning('Preencha a resposta antes de conferir.')
            else:
                acertou=conferir_treino(q,entrada)
                estado.treino_feedback=acertou
                estado.treino_total+=1
                estado.treino_acertos+=int(acertou)
                st.rerun()
        if estado.treino_feedback is not None:
            if estado.treino_feedback:
                st.success('Resposta correta!')
            else:
                st.info('Confira a resposta e use a explicação para tentar a próxima questão.')
            resposta=q['resposta']
            st.write('Resposta:',str(resposta))
            st.write(q['dica'])
            st.latex(q['formula'])
            if a:
                with st.expander('Conferir visualmente no gráfico'):
                    delta,xv,yv,raizes=calcular(a,b,c)
                    st.plotly_chart(criar_grafico(a,b,c,xv,yv,raizes),theme=None,key='treino_fig_'+chave)
    if st.button('Reiniciar placar',key='treino_reset'):
        estado.treino_acertos=0
        estado.treino_total=0
        estado.pop('treino_questao',None)
        st.rerun()
    st.divider()
    st.caption('A seguir, utilize os coeficientes do painel principal para cumprir os desafios de investigação originais.')


def render():
    st.header('Explorando parábolas')
    st.write('Explore os coeficientes ou digite os valores de um exercício para conferir a resolução.')
    st.latex(r'f(x)=ax^2+bx+c')
    controles, grafico = st.columns([1, 3])
    with controles:
        st.subheader('Coeficientes')
        modo = st.radio('Modo de utilização', ['Correção de exercícios', 'Exploração interativa'], key='q_modo')
        if modo == 'Correção de exercícios':
            st.caption('Digite cada coeficiente com seu sinal. Aceitamos inteiros, decimais (vírgula ou ponto) e frações com representação decimal de até seis casas, entre −10.000 e 10.000.')
            campos = [st.text_input(f'Coeficiente {nome}', value=padrao, key=f'q_manual_{nome}')
                      for nome, padrao in [('a','1'), ('b','-2'), ('c','-3')]]
            try:
                # Aceita vírgula decimal e ponto; não aceita separador de milhar.
                decimais = [Fraction(v.strip().replace(',', '.')) for v in campos]
                if any(abs(v) > 10000 for v in decimais):
                    raise ValueError('Use coeficientes entre -10000 e 10000.')
                if decimais[0] == 0:
                    raise ValueError('O coeficiente a deve ser diferente de zero. Com a = 0, a função não é quadrática.')
                if any(v and abs(v) < Fraction(1, 1000000) for v in decimais):
                    raise ValueError('Use coeficientes não nulos com módulo de pelo menos 0,000001.')
                # Decimais finitos até seis casas: evita exibir fórmulas inexatas.
                if any((v*1000000).denominator != 1 for v in decimais):
                    raise ValueError('Use números com até seis casas decimais.')
                a, b, c = map(float, decimais)
            except (ValueError, ZeroDivisionError, OverflowError) as erro:
                st.warning(str(erro) if str(erro).startswith(('Use ', 'O coeficiente')) else 'Preencha os três campos com números válidos.')
                return
        else:
            a = st.select_slider('Coeficiente a', options=OPCOES_A, value=1, key='q_a')
            b = st.slider('Coeficiente b', -5.0, 5.0, -2.0, 0.5, key='q_b')
            c = st.slider('Coeficiente c', -10.0, 10.0, -3.0, 0.5, key='q_c')
        escala_real = st.checkbox('Manter quadrados proporcionais', value=True, key='q_escala')
        st.caption('Desmarque para ampliar a leitura em funções muito estreitas ou largas.')
    delta, xv, yv, raizes = calcular(a,b,c)
    fig = criar_grafico(a,b,c,xv,yv,raizes,escala_real)
    with grafico:
        st.latex(latex_funcao(a,b,c))
        identificar_coeficientes(a,b,c)
        st.plotly_chart(fig, theme=None, key='q_grafico')
    painel_concavidade(a,b,c)
    st.divider()
    st.subheader('Resultados matemáticos')
    m1,m2,m3,m4 = st.columns(4)
    m1.metric('Discriminante', fmt(delta))
    m2.metric('Vértice X', fmt(xv))
    m3.metric('Vértice Y', fmt(yv))
    m4.metric('Raízes reais distintas', len(raizes))
    if raizes:
        st.write('Raízes (valores numéricos):', ', '.join(fmt(r) for r in raizes))
    else:
        st.write('A função não possui raízes reais.')
    st.write('Concavidade para cima.' if a > 0 else 'Concavidade para baixo.')
    st.divider()
    aba_resolucao, aba_estudo, aba_grafico, aba_desafios = st.tabs([
        'Aprender passo a passo', 'Estudo completo', 'Construção do gráfico', 'Treino'
    ])
    with aba_estudo:
        estudo_completo(a,b,c,delta,xv,yv,raizes)
    with aba_resolucao:
        resolucao_visual(a,b,c,delta,xv,yv,raizes,fig)
        st.subheader('Fundamentação matemática')
        st.latex(r'\Delta=b^2-4ac')
        st.latex(r'x=\frac{-b\pm\sqrt{\Delta}}{2a}\quad (\Delta\geq 0)')
        st.latex(r'V=\left(-\frac{b}{2a},-\frac{\Delta}{4a}\right)')
        st.latex(r'f(x)=a(x-x_v)^2+y_v')
    with aba_grafico:
        oficina_grafico(a,b,c,fig,raizes)
    with aba_desafios:
        painel_treino()
        desafios([
            'Construa uma parábola com duas raízes reais.',
            'Construa uma parábola com uma única raiz real.',
            'Construa uma parábola sem raízes reais.',
            'Construa uma parábola cujo vértice seja (2, 3).'
        ], status=[delta>0, delta==0, delta<0, math.isclose(xv,2,abs_tol=1e-9) and math.isclose(yv,3,abs_tol=1e-9)])
        with st.expander('Dica para o desafio 4'):
            st.latex(r'f(x)=a(x-2)^2+3')
            st.write('Experimente a = 1, b = -4 e c = 7.')


def main():
    st.set_page_config(page_title='Parábola Lab | Função quadrática', layout='wide')
    st.title('Parábola Lab')
    st.caption('Matemática & Contexto | Laboratório de funções quadráticas para o Ensino Médio')
    render()
    st.divider()
    st.caption('Matemática & Contexto — ferramenta de estudo e correção de exercícios.')


if __name__ == '__main__':
    main()
