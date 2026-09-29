import streamlit as st
from groq import Groq
from datetime import datetime
import json

st.set_page_config(page_title="Coach do Sono IA", page_icon="💤", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color:#EFF6FF; font-family:'Inter',sans-serif; }
    [data-testid="stSidebar"] { display:none; }
    .stTextInput>div>div>input, .stTextArea>div>textarea,
    .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color:#FFFFFF !important; color:#1A1A2E !important;
        border:1px solid #CED4DA !important; font-family:'Inter',sans-serif !important;
    }
    .stButton>button {
        width:100%; border-radius:10px; height:3.2em;
        background:linear-gradient(135deg,#1E3A8A,#1D4ED8) !important; color:white !important;
        font-weight:600; border:none; box-shadow:2px 2px 8px rgba(0,0,0,0.1);
        font-family:'Inter',sans-serif !important; transition:all 0.2s ease;
    }
    .stButton>button:hover { background:linear-gradient(135deg,#1D4ED8,#1E3A8A) !important; transform:translateY(-1px); }
    .stApp .stButton>button, .stApp .stButton>button p,
    .stApp .stButton>button span, .stApp .stButton>button div { color:white !important; }
    .stApp h1, .stApp h2, .stApp h3 { color:#1E3A8A !important; font-family:'Inter',sans-serif !important; font-weight:700 !important; }
    .card { background:linear-gradient(135deg,#EFF6FF,#DBEAFE); padding:20px; border-radius:14px; border:1px solid #93C5FD; margin-bottom:14px; white-space:pre-wrap; word-wrap:break-word; }
    .stApp .card, .stApp .card p, .stApp .card span, .stApp .card div, .stApp .card strong { color:#1E3A8A !important; }
    .card-blue { background:linear-gradient(135deg,#EFF6FF,#DBEAFE); padding:20px; border-radius:14px; border:1px solid #93C5FD; margin-bottom:14px; }
    .stApp .card-blue, .stApp .card-blue p, .stApp .card-blue div { color:#1E3A8A !important; }
    .card-green { background:linear-gradient(135deg,#F0FDF4,#DCFCE7); padding:20px; border-radius:14px; border:1px solid #86EFAC; margin-bottom:14px; }
    .stApp .card-green, .stApp .card-green p, .stApp .card-green div { color:#14532D !important; }
    .card-yellow { background:linear-gradient(135deg,#FFFBEB,#FEF3C7); padding:18px; border-radius:12px; border:1px solid #FCD34D; margin-bottom:12px; }
    .stApp .card-yellow, .stApp .card-yellow p, .stApp .card-yellow div { color:#78350F !important; }
    .badge { background:#1E3A8A; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .divider { border:none; height:1px; background:linear-gradient(to right,transparent,#93C5FD,transparent); margin:18px 0; }
    .stat-box { background:#FFFFFF; border-radius:12px; padding:16px; text-align:center; border:1px solid #93C5FD; }
    .stApp .stat-box div, .stApp .stat-box span { color:#1E3A8A !important; }
    .hist-item { background:#FFFFFF; border-radius:10px; padding:12px 16px; margin-bottom:8px; border-left:4px solid #93C5FD; }
    .stApp .hist-item, .stApp .hist-item p, .stApp .hist-item div { color:#1E3A8A !important; }
    </style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = (
    "Você é um especialista em medicina do sono e cronobiologia. "
    "Ajuda pessoas a melhorar a qualidade do sono com base em ciência do sono, higiene do sono e técnicas comprovadas. "
    "Nunca faz diagnósticos médicos. Português do Brasil. "
    "Responda de forma prática, detalhada e personalizada com base nas informações fornecidas."
)

@st.cache_resource
def get_cache_coach_sono():
    return {"perfis": {}}

_cache = get_cache_coach_sono()

def carregar_json_sessao(dados):
    import re as _re
    _bloq = {'api_key','etapa','nome_login','chave_login','upload_login','btn_entrar_login'}
    _pref = (
        'btn_','sel_','ul_','dl_','cad_','_sub','_sm','_tab','_bsc',
        'ativo_','rem_','chat_','duvida_','emerg_','nav_',
    )
    for k, v in dados.items():
        if k in _bloq: continue
        if any(k.startswith(p) for p in _pref): continue
        if _re.match(r'.+_\d+$', k): continue
        st.session_state[k] = v

defaults = {
    "etapa": "Login", "usuario": "", "api_key": "",
    "historico_coach_sono": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPER IA ──
def chamar_ia(prompt_montado: str, chave_hist: str, nome_aba: str, resumo: str):
    historico = st.session_state.get("historico_coach_sono", [])
    with st.spinner("🤖 A IA está analisando..."):
        try:
            client = Groq(api_key=st.session_state.api_key)
            msgs = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_montado},
            ]
            resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
            resultado = resp.choices[0].message.content
            if resultado:
                st.session_state[chave_hist] = str(resultado)
                historico.append({
                    "data": datetime.now().strftime("%d/%m %H:%M"),
                    "aba": nome_aba,
                    "resumo": resumo[:60],
                    "conteudo": resultado,
                })
                st.session_state.historico_coach_sono = historico
            return resultado
        except Exception as e:
            st.error(f"Erro na API: {e}")
            return None

# ── LOGIN ──
if st.session_state.etapa == "Login":
    st.markdown("# 💤 Coach do Sono IA")
    st.markdown("<div class='card'><b>🔒 ACESSO RESTRITO A CLIENTES DO QUIZ COM PRÊMIOS</b><br>🔗 <a href='https://quizcompremios.com.br' target='_blank' style='color:#4F46E5;font-weight:700;text-decoration:underline;'>quizcompremios.com.br</a></div>", unsafe_allow_html=True)
    st.info("💻 **Dica:** No computador a experiência é mais agradável.")
    nome  = st.text_input("Seu Nome:", key="nome_login")
    chave = st.text_input("🔑 Sua Chave API da Groq:", type="password", key="chave_login")
    arq_j = st.file_uploader("📂 Carregar dados salvos (.json):", type=["json"], key="upload_login")
    dados_login = json.load(arq_j) if arq_j else None
    if st.button("✨ ENTRAR", key="btn_entrar_login"):
        if len(nome.strip()) < 2:
            st.warning("Digite um nome com pelo menos 2 caracteres.")
        elif chave.strip():
            st.session_state.usuario = nome.strip()
            st.session_state.api_key = chave
            if dados_login:
                carregar_json_sessao(dados_login)
            st.session_state.etapa = "App"
            st.rerun()
        else:
            st.warning("Preencha nome e chave API.")

elif st.session_state.etapa == "App":
    usuario = st.session_state.usuario

    # ── BARRA SALVAR ──
    with st.expander("💾 Salvar / Carregar meus dados", expanded=False):
        _bs1, _bs2 = st.columns(2)
        with _bs1:
            _dsv = {k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith("_") and k != "api_key"}
            st.download_button("💾 Baixar dados (.json)",
                data=json.dumps(_dsv, ensure_ascii=False, indent=2, default=str),
                file_name=f"coach_sono_{st.session_state.get('usuario','user')}.json",
                mime="application/json", key="dl_sv_cs")
        with _bs2:
            _fup = st.file_uploader("📂 Carregar:", type=["json"], key="ul_sv_cs", label_visibility="collapsed")
            if _fup:
                try:
                    for _k, _v in json.loads(_fup.read().decode()).items():
                        if _k not in ("api_key","etapa"): st.session_state[_k] = _v
                    st.success("✅ Dados restaurados!"); st.rerun()
                except: st.error("Arquivo inválido.")

    (
        _tab_home, _tab_perfil, _tab_noturna, _tab_manha,
        _tab_habitos, _tab_sabotadores, _tab_plano21,
        _tab_higiene, _tab_relaxamento, _tab_diario, _tab_evolucao,
    ) = st.tabs([
        '🏠 Home', '📋 Meu Perfil', '🌙 Rotina Noturna', '☀️ Rotina Matinal',
        '📊 Hábitos', '⚠️ Sabotadores', '🗓️ Plano 21 Dias',
        '😴 Higiene', '🧘 Relaxamento', '📓 Diário', '📈 Evolução',
    ])

    # ═══════════════════════════════════════════
    # 🏠 HOME
    # ═══════════════════════════════════════════
    with _tab_home:
        st.title(f"💤 Olá, {usuario}!")
        st.markdown("*Durma melhor, viva mais — seu coach de sono com IA.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown("<div class='stat-box'><div style='font-size:1.8em;'>🌙</div><div>Rotinas do Sono</div></div>", unsafe_allow_html=True)
        with c2: st.markdown("<div class='stat-box'><div style='font-size:1.8em;'>🤖</div><div>Powered by IA</div></div>", unsafe_allow_html=True)
        with c3: st.markdown("<div class='stat-box'><div style='font-size:1.8em;'>📈</div><div>Acompanhe Evolução</div></div>", unsafe_allow_html=True)
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='card-blue'>Use as abas acima para navegar. Cada aba tem um formulário guiado — preencha as perguntas e a IA gera um plano personalizado para você.</div>", unsafe_allow_html=True)

        historico = st.session_state.get("historico_coach_sono", [])
        if historico:
            st.markdown("### 📋 Últimas análises")
            for item in reversed(historico[-5:]):
                st.markdown(f"<div class='hist-item'><b>{item['data']} — {item['aba']}</b><br>{item['resumo']}...</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════
    # 📋 MEU PERFIL DO SONO
    # ═══════════════════════════════════════════
    with _tab_perfil:
        st.header("📋 Meu Perfil do Sono")
        st.markdown("Responda as perguntas abaixo e a IA vai montar seu perfil de sono personalizado.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            idade_perf = st.number_input("Sua idade:", min_value=10, max_value=100, value=st.session_state.get("idade_perf", 35), key="idade_perf")
            sexo_perf = st.selectbox("Sexo biológico:", ["Feminino", "Masculino", "Prefiro não dizer"], key="sexo_perf", index=["Feminino","Masculino","Prefiro não dizer"].index(st.session_state.get("sexo_perf","Feminino")))
            cronotipo_perf = st.selectbox("Você se considera:", ["🦅 Matutino (acorda cedo naturalmente)", "🦉 Vespertino (prefere acordar tarde)", "🐦 Intermediário (sem preferência)"], key="cronotipo_perf")
        with c2:
            horas_dorme_perf = st.number_input("Quantas horas dorme por noite (em média):", min_value=2, max_value=14, value=st.session_state.get("horas_dorme_perf", 6), key="horas_dorme_perf")
            qualidade_perf = st.select_slider("Qualidade do seu sono (1=péssimo, 10=ótimo):", options=list(range(1,11)), value=st.session_state.get("qualidade_perf", 5), key="qualidade_perf")
            cansaco_dia_perf = st.radio("Acorda cansado?", ["Nunca", "Às vezes", "Quase sempre", "Sempre"], horizontal=True, key="cansaco_dia_perf", index=["Nunca","Às vezes","Quase sempre","Sempre"].index(st.session_state.get("cansaco_dia_perf","Às vezes")))

        problemas_perf = st.multiselect("Quais problemas você tem com o sono?",
            ["Demoro a pegar no sono", "Acordo no meio da noite", "Acordo muito cedo", "Sono agitado / pesadelos",
             "Ronco / apneia", "Bruxismo (ranger dentes)", "Síndrome das pernas inquietas", "Paralisia do sono"],
            default=st.session_state.get("problemas_perf", []), key="problemas_perf")

        condicoes_perf = st.multiselect("Tem alguma dessas condições?",
            ["Ansiedade", "Depressão", "Estresse crônico", "Hipertensão", "Diabetes", "Hipotireoidismo", "Nenhuma"],
            default=st.session_state.get("condicoes_perf", ["Nenhuma"]), key="condicoes_perf")

        obs_perf = st.text_area("Algo mais que queira compartilhar (opcional):", height=80, key="obs_perf",
            placeholder="Ex: tomo remédio para dormir, trabalho à noite, tenho bebê recém-nascido...")

        if st.button("🤖 GERAR MEU PERFIL DO SONO", key="btn_perfil_sono", use_container_width=True):
            probs = ", ".join(problemas_perf) if problemas_perf else "nenhum problema específico relatado"
            conds = ", ".join(condicoes_perf) if condicoes_perf else "nenhuma"
            prompt = (
                f"Monte um perfil detalhado de sono para esta pessoa:\n"
                f"- Idade: {idade_perf} anos | Sexo: {sexo_perf}\n"
                f"- Cronotipo: {cronotipo_perf}\n"
                f"- Horas de sono por noite: {horas_dorme_perf}h | Qualidade percebida: {qualidade_perf}/10\n"
                f"- Acorda cansado: {cansaco_dia_perf}\n"
                f"- Problemas: {probs}\n"
                f"- Condições de saúde: {conds}\n"
                f"- Observações: {obs_perf or 'nenhuma'}\n\n"
                f"Identifique o perfil do sono, os pontos críticos e prioridades de melhoria."
            )
            res = chamar_ia(prompt, "res_perfil_sono", "Meu Perfil do Sono", f"{idade_perf}a | {qualidade_perf}/10 | {probs[:40]}")
            if res:
                st.session_state["res_perfil_sono"] = res

        if st.session_state.get("res_perfil_sono"):
            st.markdown(f"<div class='card'>{st.session_state['res_perfil_sono']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_perfil_sono"],
                file_name="perfil_sono.txt", mime="text/plain", key="dl_perfil_sono")

    # ═══════════════════════════════════════════
    # 🌙 ROTINA NOTURNA
    # ═══════════════════════════════════════════
    with _tab_noturna:
        st.header("🌙 Rotina Noturna")
        st.markdown("Preencha seus hábitos noturnos e receba uma rotina personalizada.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            hora_dormir_rn = st.selectbox("Que horas costuma ir para cama?",
                ["Antes das 21h","21h–22h","22h–23h","23h–00h","00h–01h","Depois da 01h"],
                index=["Antes das 21h","21h–22h","22h–23h","23h–00h","00h–01h","Depois da 01h"].index(st.session_state.get("hora_dormir_rn","23h–00h")),
                key="hora_dormir_rn")
            tempo_pegar_sono_rn = st.selectbox("Quanto tempo leva para pegar no sono?",
                ["Menos de 10 min","10–20 min","20–30 min","30–60 min","Mais de 1 hora"],
                index=["Menos de 10 min","10–20 min","20–30 min","30–60 min","Mais de 1 hora"].index(st.session_state.get("tempo_pegar_sono_rn","20–30 min")),
                key="tempo_pegar_sono_rn")
            luz_tela_rn = st.radio("Usa telas (celular/TV) antes de dormir?",
                ["Não uso","Paro 1h antes","Paro 30 min antes","Uso até na cama"],
                horizontal=False, key="luz_tela_rn",
                index=["Não uso","Paro 1h antes","Paro 30 min antes","Uso até na cama"].index(st.session_state.get("luz_tela_rn","Uso até na cama")))
        with c2:
            cafe_noite_rn = st.radio("Toma café/energético à noite?",
                ["Nunca","Raramente","Às vezes (após 18h)","Frequentemente (após 18h)"],
                horizontal=False, key="cafe_noite_rn",
                index=["Nunca","Raramente","Às vezes (após 18h)","Frequentemente (após 18h)"].index(st.session_state.get("cafe_noite_rn","Às vezes (após 18h)")))
            alcool_rn = st.radio("Bebe álcool à noite?",
                ["Nunca","Raramente","1–2x por semana","Quase todo dia"],
                horizontal=False, key="alcool_rn",
                index=["Nunca","Raramente","1–2x por semana","Quase todo dia"].index(st.session_state.get("alcool_rn","Raramente")))
            jantar_rn = st.selectbox("Jantar: quanto tempo antes de dormir?",
                ["Mais de 3h","2–3h","1–2h","Menos de 1h","Não janto"],
                index=["Mais de 3h","2–3h","1–2h","Menos de 1h","Não janto"].index(st.session_state.get("jantar_rn","1–2h")),
                key="jantar_rn")

        ritual_rn = st.multiselect("O que faz antes de dormir?",
            ["Tomo banho quente","Leio livro","Meditação/respiração","Ouço música calma",
             "Faço exercícios","Trabalho/estudo","Fico nas redes sociais","Assisto séries",
             "Rezo/ora","Nada especial"],
            default=st.session_state.get("ritual_rn", []), key="ritual_rn")

        ambiente_rn = st.multiselect("Como é o ambiente do quarto?",
            ["Escuro","Com luz acesa","Silencioso","Com barulho","Temperatura fresca","Temperatura quente","TV ligada"],
            default=st.session_state.get("ambiente_rn", ["Escuro","Silencioso"]), key="ambiente_rn")

        objetivo_rn = st.text_input("Qual seu principal objetivo com a rotina noturna?",
            value=st.session_state.get("objetivo_rn",""),
            placeholder="Ex: pegar no sono mais rápido, parar de acordar às 3h...", key="objetivo_rn")

        if st.button("🤖 CRIAR MINHA ROTINA NOTURNA", key="btn_rotina_noturna", use_container_width=True):
            ritual = ", ".join(ritual_rn) if ritual_rn else "sem ritual definido"
            amb = ", ".join(ambiente_rn) if ambiente_rn else "não informado"
            prompt = (
                f"Crie uma rotina noturna personalizada e detalhada para esta pessoa:\n"
                f"- Horário de ir para cama: {hora_dormir_rn}\n"
                f"- Tempo para pegar no sono: {tempo_pegar_sono_rn}\n"
                f"- Uso de telas: {luz_tela_rn}\n"
                f"- Cafeína à noite: {cafe_noite_rn}\n"
                f"- Álcool: {alcool_rn}\n"
                f"- Jantar: {jantar_rn} antes de dormir\n"
                f"- Ritual atual: {ritual}\n"
                f"- Ambiente do quarto: {amb}\n"
                f"- Objetivo: {objetivo_rn or 'melhorar o sono em geral'}\n\n"
                f"Monte uma rotina hora a hora para as 2h antes de dormir, com justificativas científicas."
            )
            res = chamar_ia(prompt, "res_rotina_noturna", "Rotina Noturna", f"{hora_dormir_rn} | {tempo_pegar_sono_rn}")
            if res:
                st.session_state["res_rotina_noturna"] = res

        if st.session_state.get("res_rotina_noturna"):
            st.markdown(f"<div class='card'>{st.session_state['res_rotina_noturna']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar rotina noturna", data=st.session_state["res_rotina_noturna"],
                file_name="rotina_noturna.txt", mime="text/plain", key="dl_rotina_noturna")

    # ═══════════════════════════════════════════
    # ☀️ ROTINA MATINAL
    # ═══════════════════════════════════════════
    with _tab_manha:
        st.header("☀️ Rotina Matinal")
        st.markdown("Preencha seus hábitos matinais e receba uma rotina de início de dia que potencializa o sono.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            hora_acorda_rm = st.selectbox("Que horas costuma acordar?",
                ["Antes das 5h","5h–6h","6h–7h","7h–8h","8h–9h","Depois das 9h"],
                index=["Antes das 5h","5h–6h","6h–7h","7h–8h","8h–9h","Depois das 9h"].index(st.session_state.get("hora_acorda_rm","6h–7h")),
                key="hora_acorda_rm")
            alarme_rm = st.radio("Como acorda?",
                ["Naturalmente (sem alarme)","1 alarme","2–3 alarmes","Muitos alarmes (cochila)"],
                horizontal=False, key="alarme_rm",
                index=["Naturalmente (sem alarme)","1 alarme","2–3 alarmes","Muitos alarmes (cochila)"].index(st.session_state.get("alarme_rm","2–3 alarmes")))
            humor_acorda_rm = st.select_slider("Humor ao acordar (1=péssimo, 10=ótimo):",
                options=list(range(1,11)), value=st.session_state.get("humor_acorda_rm",4), key="humor_acorda_rm")
        with c2:
            celular_manha_rm = st.radio("Pega no celular ao acordar?",
                ["Não","Depois de 30 min","Imediatamente"],
                horizontal=False, key="celular_manha_rm",
                index=["Não","Depois de 30 min","Imediatamente"].index(st.session_state.get("celular_manha_rm","Imediatamente")))
            luz_solar_rm = st.radio("Se expõe à luz solar de manhã?",
                ["Sim, logo ao acordar","Às vezes","Raramente","Nunca"],
                horizontal=False, key="luz_solar_rm",
                index=["Sim, logo ao acordar","Às vezes","Raramente","Nunca"].index(st.session_state.get("luz_solar_rm","Raramente")))
            cafe_manha_rm = st.radio("Café da manhã: quando toma?",
                ["Logo ao acordar","30–60 min após","Depois de 90 min","Não tomo"],
                horizontal=False, key="cafe_manha_rm",
                index=["Logo ao acordar","30–60 min após","Depois de 90 min","Não tomo"].index(st.session_state.get("cafe_manha_rm","Logo ao acordar")))

        atividades_rm = st.multiselect("O que faz nas primeiras 2h do dia?",
            ["Exercício físico","Meditação","Leitura","Estudo/trabalho","Redes sociais",
             "Televisão","Cuido da família","Banho quente","Banho frio","Café tranquilo"],
            default=st.session_state.get("atividades_rm", []), key="atividades_rm")

        objetivo_rm = st.text_input("O que quer melhorar na manhã?",
            value=st.session_state.get("objetivo_rm",""),
            placeholder="Ex: acordar com mais energia, parar de usar alarme...", key="objetivo_rm")

        if st.button("🤖 CRIAR MINHA ROTINA MATINAL", key="btn_rotina_manha", use_container_width=True):
            ativs = ", ".join(atividades_rm) if atividades_rm else "nenhuma rotina definida"
            prompt = (
                f"Crie uma rotina matinal personalizada para otimizar energia e qualidade do sono noturno:\n"
                f"- Horário de acordar: {hora_acorda_rm}\n"
                f"- Como acorda: {alarme_rm}\n"
                f"- Humor ao acordar: {humor_acorda_rm}/10\n"
                f"- Celular pela manhã: {celular_manha_rm}\n"
                f"- Luz solar: {luz_solar_rm}\n"
                f"- Café: {cafe_manha_rm}\n"
                f"- Atividades matinais: {ativs}\n"
                f"- Objetivo: {objetivo_rm or 'mais energia e disposição'}\n\n"
                f"Monte uma rotina matinal hora a hora com base na ciência do sono e cronobiologia."
            )
            res = chamar_ia(prompt, "res_rotina_manha", "Rotina Matinal", f"{hora_acorda_rm} | humor {humor_acorda_rm}/10")
            if res:
                st.session_state["res_rotina_manha"] = res

        if st.session_state.get("res_rotina_manha"):
            st.markdown(f"<div class='card'>{st.session_state['res_rotina_manha']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar rotina matinal", data=st.session_state["res_rotina_manha"],
                file_name="rotina_matinal.txt", mime="text/plain", key="dl_rotina_manha")

    # ═══════════════════════════════════════════
    # 📊 ANÁLISE DE HÁBITOS
    # ═══════════════════════════════════════════
    with _tab_habitos:
        st.header("📊 Análise de Hábitos do Sono")
        st.markdown("Responda sobre seus hábitos diários e receba uma análise do impacto no sono.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            exercicio_hb = st.selectbox("Frequência de exercício físico:",
                ["Não pratico","1x por semana","2–3x por semana","4–5x por semana","Todo dia"],
                index=["Não pratico","1x por semana","2–3x por semana","4–5x por semana","Todo dia"].index(st.session_state.get("exercicio_hb","2–3x por semana")),
                key="exercicio_hb")
            horario_exercicio_hb = st.radio("Quando se exercita?",
                ["Manhã","Tarde","Noite (após 19h)","Não pratico"],
                horizontal=True, key="horario_exercicio_hb",
                index=["Manhã","Tarde","Noite (após 19h)","Não pratico"].index(st.session_state.get("horario_exercicio_hb","Tarde")))
            estresse_hb = st.select_slider("Nível de estresse no dia a dia (1–10):",
                options=list(range(1,11)), value=st.session_state.get("estresse_hb",6), key="estresse_hb")
        with c2:
            agua_hb = st.selectbox("Hidratação diária:",
                ["Menos de 1L","1–1,5L","1,5–2L","2–3L","Mais de 3L"],
                index=["Menos de 1L","1–1,5L","1,5–2L","2–3L","Mais de 3L"].index(st.session_state.get("agua_hb","1,5–2L")),
                key="agua_hb")
            sesta_hb = st.radio("Tira soneca durante o dia?",
                ["Nunca","Raramente","1–2x por semana","Quase todo dia","Todo dia (mais de 30 min)"],
                horizontal=False, key="sesta_hb",
                index=["Nunca","Raramente","1–2x por semana","Quase todo dia","Todo dia (mais de 30 min)"].index(st.session_state.get("sesta_hb","Raramente")))
            trabalho_hb = st.radio("Trabalha ou estuda à noite?",
                ["Nunca","Às vezes","Frequentemente","Todo dia"],
                horizontal=True, key="trabalho_hb",
                index=["Nunca","Às vezes","Frequentemente","Todo dia"].index(st.session_state.get("trabalho_hb","Às vezes")))

        alimentacao_hb = st.multiselect("Hábitos alimentares que interferem no sono:",
            ["Muito açúcar à noite","Refeições pesadas à noite","Fico com fome antes de dormir",
             "Bebo muito líquido à noite","Uso suplementos (magnésio, melatonina...)",
             "Alimentação equilibrada","Não identifico problema alimentar"],
            default=st.session_state.get("alimentacao_hb", []), key="alimentacao_hb")

        if st.button("🤖 ANALISAR MEUS HÁBITOS", key="btn_habitos_sono", use_container_width=True):
            alim = ", ".join(alimentacao_hb) if alimentacao_hb else "não identificado"
            prompt = (
                f"Analise os hábitos diários desta pessoa e o impacto no sono:\n"
                f"- Exercício: {exercicio_hb} | Horário: {horario_exercicio_hb}\n"
                f"- Estresse: {estresse_hb}/10\n"
                f"- Hidratação: {agua_hb}\n"
                f"- Soneca: {sesta_hb}\n"
                f"- Trabalho noturno: {trabalho_hb}\n"
                f"- Alimentação: {alim}\n\n"
                f"Identifique os hábitos que mais prejudicam o sono, explique o porquê e dê recomendações práticas."
            )
            res = chamar_ia(prompt, "res_habitos_sono", "Análise de Hábitos", f"Estresse {estresse_hb}/10 | {exercicio_hb}")
            if res:
                st.session_state["res_habitos_sono"] = res

        if st.session_state.get("res_habitos_sono"):
            st.markdown(f"<div class='card'>{st.session_state['res_habitos_sono']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar análise", data=st.session_state["res_habitos_sono"],
                file_name="analise_habitos.txt", mime="text/plain", key="dl_habitos_sono")

    # ═══════════════════════════════════════════
    # ⚠️ SABOTADORES
    # ═══════════════════════════════════════════
    with _tab_sabotadores:
        st.header("⚠️ Sabotadores do Sono")
        st.markdown("Identifique o que está destruindo seu sono e receba estratégias para eliminar cada sabotador.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        sabotadores_principais = st.multiselect(
            "Quais sabotadores você reconhece em você?",
            ["📱 Telas antes de dormir","☕ Cafeína no período da tarde/noite",
             "🍷 Álcool","🍕 Alimentação pesada à noite","💡 Quarto com muita luz",
             "🔊 Barulho excessivo","🌡️ Temperatura inadequada","😰 Ansiedade / ruminação mental",
             "📋 Muitas responsabilidades / estresse","🛋️ Cama usada para trabalho/TV",
             "⏰ Horários irregulares (dorme horas diferentes todo dia)",
             "😴 Sonecas longas durante o dia","💊 Uso de remédios estimulantes","🚬 Tabagismo"],
            default=st.session_state.get("sabotadores_principais", []),
            key="sabotadores_principais"
        )

        c1, c2 = st.columns(2)
        with c1:
            pior_sabotador = st.selectbox("Qual você considera o PIOR para você?",
                ["📱 Telas antes de dormir","☕ Cafeína","🍷 Álcool","😰 Ansiedade/estresse",
                 "⏰ Horários irregulares","🔊 Barulho","💡 Luz no quarto","Outro"],
                index=["📱 Telas antes de dormir","☕ Cafeína","🍷 Álcool","😰 Ansiedade/estresse",
                       "⏰ Horários irregulares","🔊 Barulho","💡 Luz no quarto","Outro"].index(
                           st.session_state.get("pior_sabotador","😰 Ansiedade/estresse")),
                key="pior_sabotador")
            tentou_resolver_sb = st.radio("Já tentou resolver?",
                ["Ainda não tentei","Tentei mas não consegui","Consigo às vezes","Já melhorei bastante"],
                horizontal=False, key="tentou_resolver_sb",
                index=["Ainda não tentei","Tentei mas não consegui","Consigo às vezes","Já melhorei bastante"].index(
                    st.session_state.get("tentou_resolver_sb","Tentei mas não consegui")))
        with c2:
            motivacao_sb = st.select_slider("Sua motivação para mudar (1–10):",
                options=list(range(1,11)), value=st.session_state.get("motivacao_sb", 7), key="motivacao_sb")
            disponibilidade_sb = st.radio("Disponibilidade para mudança:",
                ["Posso mudar tudo agora","Posso mudar algumas coisas","Tenho muitas limitações"],
                horizontal=False, key="disponibilidade_sb",
                index=["Posso mudar tudo agora","Posso mudar algumas coisas","Tenho muitas limitações"].index(
                    st.session_state.get("disponibilidade_sb","Posso mudar algumas coisas")))

        contexto_sb = st.text_area("Contexto adicional sobre seus sabotadores (opcional):",
            height=80, key="contexto_sb",
            value=st.session_state.get("contexto_sb",""),
            placeholder="Ex: trabalho em turno noturno, tenho filhos pequenos, moro em rua barulhenta...")

        if st.button("🤖 CRIAR PLANO ANTI-SABOTADORES", key="btn_sabotadores", use_container_width=True):
            sabs = ", ".join(sabotadores_principais) if sabotadores_principais else "não identificados"
            prompt = (
                f"Analise os sabotadores do sono desta pessoa e crie um plano de ação:\n"
                f"- Sabotadores identificados: {sabs}\n"
                f"- Pior sabotador: {pior_sabotador}\n"
                f"- Tentativa anterior: {tentou_resolver_sb}\n"
                f"- Motivação: {motivacao_sb}/10\n"
                f"- Disponibilidade: {disponibilidade_sb}\n"
                f"- Contexto: {contexto_sb or 'nenhum'}\n\n"
                f"Para cada sabotador listado, explique o impacto científico no sono e dê 3 estratégias práticas e progressivas para eliminar."
            )
            res = chamar_ia(prompt, "res_sabotadores", "Sabotadores", f"{pior_sabotador} | motivação {motivacao_sb}/10")
            if res:
                st.session_state["res_sabotadores"] = res

        if st.session_state.get("res_sabotadores"):
            st.markdown(f"<div class='card'>{st.session_state['res_sabotadores']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar plano", data=st.session_state["res_sabotadores"],
                file_name="plano_sabotadores.txt", mime="text/plain", key="dl_sabotadores")

    # ═══════════════════════════════════════════
    # 🗓️ PLANO 21 DIAS
    # ═══════════════════════════════════════════
    with _tab_plano21:
        st.header("🗓️ Plano 21 Dias para Transformar o Sono")
        st.markdown("Preencha suas metas e receba um plano progressivo de 21 dias.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            meta_principal_p21 = st.selectbox("Sua meta principal:",
                ["Pegar no sono mais rápido","Dormir mais horas","Parar de acordar à noite",
                 "Acordar mais descansado","Eliminar ronco/apneia","Ter horário fixo de dormir",
                 "Reduzir dependência de remédio para dormir","Melhorar humor/energia de dia"],
                index=["Pegar no sono mais rápido","Dormir mais horas","Parar de acordar à noite",
                       "Acordar mais descansado","Eliminar ronco/apneia","Ter horário fixo de dormir",
                       "Reduzir dependência de remédio para dormir","Melhorar humor/energia de dia"].index(
                           st.session_state.get("meta_principal_p21","Acordar mais descansado")),
                key="meta_principal_p21")
            horas_meta_p21 = st.number_input("Quantas horas quer dormir por noite:",
                min_value=5, max_value=10, value=st.session_state.get("horas_meta_p21", 8), key="horas_meta_p21")
            horario_dormir_meta_p21 = st.selectbox("Horário ideal para dormir:",
                ["21h–22h","22h–23h","23h–00h","00h–01h"],
                index=["21h–22h","22h–23h","23h–00h","00h–01h"].index(st.session_state.get("horario_dormir_meta_p21","23h–00h")),
                key="horario_dormir_meta_p21")
        with c2:
            horario_acordar_meta_p21 = st.selectbox("Horário ideal para acordar:",
                ["5h–6h","6h–7h","7h–8h","8h–9h","9h–10h"],
                index=["5h–6h","6h–7h","7h–8h","8h–9h","9h–10h"].index(st.session_state.get("horario_acordar_meta_p21","6h–7h")),
                key="horario_acordar_meta_p21")
            comprometimento_p21 = st.select_slider("Nível de comprometimento (1–10):",
                options=list(range(1,11)), value=st.session_state.get("comprometimento_p21", 8), key="comprometimento_p21")
            restricoes_p21 = st.radio("Restrições importantes:",
                ["Sem restrições","Trabalho em turnos","Tenho filhos pequenos","Condição médica limitante"],
                horizontal=False, key="restricoes_p21",
                index=["Sem restrições","Trabalho em turnos","Tenho filhos pequenos","Condição médica limitante"].index(
                    st.session_state.get("restricoes_p21","Sem restrições")))

        mudancas_aceitar_p21 = st.multiselect("O que está disposto a mudar?",
            ["Horário de dormir fixo","Parar telas 1h antes","Sem cafeína após 14h",
             "Exercício regular","Ritual de relaxamento noturno","Quarto mais escuro/silencioso",
             "Alimentação mais leve à noite","Reduzir álcool","Sem soneca longa"],
            default=st.session_state.get("mudancas_aceitar_p21", []), key="mudancas_aceitar_p21")

        if st.button("🤖 CRIAR MEU PLANO DE 21 DIAS", key="btn_plano21", use_container_width=True):
            muda = ", ".join(mudancas_aceitar_p21) if mudancas_aceitar_p21 else "a definir"
            prompt = (
                f"Crie um plano de 21 dias progressivo para transformar o sono desta pessoa:\n"
                f"- Meta principal: {meta_principal_p21}\n"
                f"- Horas de sono desejadas: {horas_meta_p21}h\n"
                f"- Horário dormir: {horario_dormir_meta_p21} | Acordar: {horario_acordar_meta_p21}\n"
                f"- Comprometimento: {comprometimento_p21}/10\n"
                f"- Restrições: {restricoes_p21}\n"
                f"- Mudanças aceitas: {muda}\n\n"
                f"Divida o plano em 3 semanas (semanas 1, 2 e 3) com metas e ações específicas para cada. "
                f"Use progressão gradual: semana 1 mais fácil, semana 3 consolidação."
            )
            res = chamar_ia(prompt, "res_plano21", "Plano 21 Dias", f"{meta_principal_p21} | {horas_meta_p21}h")
            if res:
                st.session_state["res_plano21"] = res

        if st.session_state.get("res_plano21"):
            st.markdown(f"<div class='card'>{st.session_state['res_plano21']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar plano 21 dias", data=st.session_state["res_plano21"],
                file_name="plano_21_dias.txt", mime="text/plain", key="dl_plano21")

    # ═══════════════════════════════════════════
    # 😴 HIGIENE DO SONO
    # ═══════════════════════════════════════════
    with _tab_higiene:
        st.header("😴 Higiene do Sono")
        st.markdown("Avalie sua higiene do sono atual e receba orientações para otimizar.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        st.markdown("**Avalie cada aspecto da sua higiene do sono:**")
        c1, c2 = st.columns(2)
        with c1:
            quarto_escuro_hig = st.radio("Quarto: escuridão ao dormir?",
                ["Completamente escuro","Pouca luz","Luz moderada","Muito iluminado"],
                horizontal=False, key="quarto_escuro_hig",
                index=["Completamente escuro","Pouca luz","Luz moderada","Muito iluminado"].index(
                    st.session_state.get("quarto_escuro_hig","Pouca luz")))
            temperatura_hig = st.radio("Temperatura do quarto:",
                ["Fresca (18–21°C — ideal)","Agradável mas não fresca","Quente","Muito quente/fria"],
                horizontal=False, key="temperatura_hig",
                index=["Fresca (18–21°C — ideal)","Agradável mas não fresca","Quente","Muito quente/fria"].index(
                    st.session_state.get("temperatura_hig","Quente")))
            ruido_hig = st.radio("Ruído no quarto:",
                ["Silencioso","Ruído leve (fan/AC)","Barulhento","Muito barulhento"],
                horizontal=False, key="ruido_hig",
                index=["Silencioso","Ruído leve (fan/AC)","Barulhento","Muito barulhento"].index(
                    st.session_state.get("ruido_hig","Barulhento")))
        with c2:
            cama_uso_hig = st.multiselect("A cama é usada apenas para dormir?",
                ["Só durmo na cama","Uso para trabalhar","Uso para assistir TV","Uso para ficar no celular","Uso para comer"],
                default=st.session_state.get("cama_uso_hig",["Só durmo na cama"]), key="cama_uso_hig")
            roupa_cama_hig = st.radio("Troca roupas de cama frequentemente?",
                ["Semanalmente","A cada 2 semanas","Mensalmente","Raramente"],
                horizontal=False, key="roupa_cama_hig",
                index=["Semanalmente","A cada 2 semanas","Mensalmente","Raramente"].index(
                    st.session_state.get("roupa_cama_hig","A cada 2 semanas")))
            colchao_hig = st.radio("Qualidade do colchão/travesseiro:",
                ["Excelente","Bom","Regular","Ruim/desconfortável"],
                horizontal=False, key="colchao_hig",
                index=["Excelente","Bom","Regular","Ruim/desconfortável"].index(
                    st.session_state.get("colchao_hig","Regular")))

        horario_regular_hig = st.radio("Tem horário fixo para dormir/acordar?",
            ["Sim, sempre o mesmo horário","Varia até 30 min","Varia 1h ou mais","Completamente irregular"],
            horizontal=True, key="horario_regular_hig",
            index=["Sim, sempre o mesmo horário","Varia até 30 min","Varia 1h ou mais","Completamente irregular"].index(
                st.session_state.get("horario_regular_hig","Varia 1h ou mais")))

        if st.button("🤖 AVALIAR MINHA HIGIENE DO SONO", key="btn_higiene", use_container_width=True):
            usos_cama = ", ".join(cama_uso_hig) if cama_uso_hig else "não informado"
            prompt = (
                f"Avalie a higiene do sono desta pessoa e dê recomendações práticas:\n"
                f"- Escuridão do quarto: {quarto_escuro_hig}\n"
                f"- Temperatura: {temperatura_hig}\n"
                f"- Ruído: {ruido_hig}\n"
                f"- Uso da cama: {usos_cama}\n"
                f"- Troca de roupas de cama: {roupa_cama_hig}\n"
                f"- Colchão/travesseiro: {colchao_hig}\n"
                f"- Regularidade de horário: {horario_regular_hig}\n\n"
                f"Identifique pontos críticos, atribua uma nota de higiene do sono (0–100) e dê um plano de melhoria prioritizado."
            )
            res = chamar_ia(prompt, "res_higiene", "Higiene do Sono", f"Quarto: {quarto_escuro_hig} | {temperatura_hig}")
            if res:
                st.session_state["res_higiene"] = res

        if st.session_state.get("res_higiene"):
            st.markdown(f"<div class='card'>{st.session_state['res_higiene']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar avaliação", data=st.session_state["res_higiene"],
                file_name="higiene_sono.txt", mime="text/plain", key="dl_higiene")

    # ═══════════════════════════════════════════
    # 🧘 TÉCNICAS DE RELAXAMENTO
    # ═══════════════════════════════════════════
    with _tab_relaxamento:
        st.header("🧘 Técnicas de Relaxamento")
        st.markdown("Descubra as técnicas ideais para você desligar a mente e relaxar o corpo.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            dificuldade_rlx = st.selectbox("Principal dificuldade para relaxar:",
                ["Mente acelerada com pensamentos","Tensão muscular / dores","Ansiedade e preocupações",
                 "Incapacidade de 'desligar' o trabalho","Sensação de agitação física","Misto de tudo"],
                index=["Mente acelerada com pensamentos","Tensão muscular / dores","Ansiedade e preocupações",
                       "Incapacidade de 'desligar' o trabalho","Sensação de agitação física","Misto de tudo"].index(
                           st.session_state.get("dificuldade_rlx","Mente acelerada com pensamentos")),
                key="dificuldade_rlx")
            tempo_disposto_rlx = st.radio("Tempo disponível para relaxamento:",
                ["5 minutos","10–15 minutos","20–30 minutos","Mais de 30 minutos"],
                horizontal=True, key="tempo_disposto_rlx",
                index=["5 minutos","10–15 minutos","20–30 minutos","Mais de 30 minutos"].index(
                    st.session_state.get("tempo_disposto_rlx","10–15 minutos")))
        with c2:
            experiencia_rlx = st.multiselect("Já tentou alguma dessas técnicas?",
                ["Respiração 4-7-8","Relaxamento muscular progressivo","Meditação guiada",
                 "Yoga / alongamento","ASMR","Sons da natureza","Body scan","Nenhuma"],
                default=st.session_state.get("experiencia_rlx", ["Nenhuma"]), key="experiencia_rlx")
            preferencia_rlx = st.multiselect("Prefere técnicas que sejam:",
                ["Silenciosas","Com áudio guiado","Físicas (corpo)","Mentais (visualização)",
                 "Rápidas (< 10 min)","Relaxantes progressivas"],
                default=st.session_state.get("preferencia_rlx", []), key="preferencia_rlx")

        contexto_rlx = st.radio("Onde vai praticar?",
            ["Na cama antes de dormir","No sofá","No chão","Em qualquer lugar"],
            horizontal=True, key="contexto_rlx",
            index=["Na cama antes de dormir","No sofá","No chão","Em qualquer lugar"].index(
                st.session_state.get("contexto_rlx","Na cama antes de dormir")))

        if st.button("🤖 CRIAR PROTOCOLO DE RELAXAMENTO", key="btn_relaxamento", use_container_width=True):
            exp = ", ".join(experiencia_rlx) if experiencia_rlx else "nenhuma"
            pref = ", ".join(preferencia_rlx) if preferencia_rlx else "sem preferência"
            prompt = (
                f"Crie um protocolo de relaxamento personalizado para pré-sono:\n"
                f"- Principal dificuldade: {dificuldade_rlx}\n"
                f"- Tempo disponível: {tempo_disposto_rlx}\n"
                f"- Técnicas já testadas: {exp}\n"
                f"- Preferências: {pref}\n"
                f"- Local de prática: {contexto_rlx}\n\n"
                f"Recomende 3 técnicas específicas com instruções passo a passo detalhadas, "
                f"indicando qual fazer primeiro e por quê."
            )
            res = chamar_ia(prompt, "res_relaxamento", "Técnicas de Relaxamento", f"{dificuldade_rlx} | {tempo_disposto_rlx}")
            if res:
                st.session_state["res_relaxamento"] = res

        if st.session_state.get("res_relaxamento"):
            st.markdown(f"<div class='card'>{st.session_state['res_relaxamento']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar protocolo", data=st.session_state["res_relaxamento"],
                file_name="protocolo_relaxamento.txt", mime="text/plain", key="dl_relaxamento")

    # ═══════════════════════════════════════════
    # 📓 DIÁRIO DO SONO
    # ═══════════════════════════════════════════
    with _tab_diario:
        st.header("📓 Diário do Sono")
        st.markdown("Registre como foi sua noite de sono e receba uma análise e dicas.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        st.markdown("**Registre sua noite:**")
        c1, c2 = st.columns(2)
        with c1:
            data_diario = st.date_input("Data (noite registrada):", key="data_diario")
            hora_deitou_d = st.selectbox("Que horas foi para a cama:",
                ["Antes das 21h","21h–22h","22h–23h","23h–00h","00h–01h","Depois da 01h"],
                index=["Antes das 21h","21h–22h","22h–23h","23h–00h","00h–01h","Depois da 01h"].index(
                    st.session_state.get("hora_deitou_d","23h–00h")),
                key="hora_deitou_d")
            hora_dormiu_d = st.selectbox("Que horas pegou no sono (estimado):",
                ["Antes das 21h","21h–22h","22h–23h","23h–00h","00h–01h","01h–02h","Depois das 02h"],
                index=["Antes das 21h","21h–22h","22h–23h","23h–00h","00h–01h","01h–02h","Depois das 02h"].index(
                    st.session_state.get("hora_dormiu_d","00h–01h")),
                key="hora_dormiu_d")
            hora_acordou_d = st.selectbox("Que horas acordou:",
                ["Antes das 5h","5h–6h","6h–7h","7h–8h","8h–9h","Depois das 9h"],
                index=["Antes das 5h","5h–6h","6h–7h","7h–8h","8h–9h","Depois das 9h"].index(
                    st.session_state.get("hora_acordou_d","6h–7h")),
                key="hora_acordou_d")
        with c2:
            qualidade_noite_d = st.select_slider("Qualidade da noite (1–10):",
                options=list(range(1,11)), value=st.session_state.get("qualidade_noite_d",5), key="qualidade_noite_d")
            vezes_acordou_d = st.number_input("Quantas vezes acordou durante a noite:",
                min_value=0, max_value=20, value=st.session_state.get("vezes_acordou_d",1), key="vezes_acordou_d")
            disposicao_manha_d = st.select_slider("Disposição ao acordar (1–10):",
                options=list(range(1,11)), value=st.session_state.get("disposicao_manha_d",4), key="disposicao_manha_d")
            sonhos_d = st.radio("Teve sonhos ou pesadelos?",
                ["Não lembro","Sonhos normais","Pesadelos","Sono agitado"],
                horizontal=True, key="sonhos_d",
                index=["Não lembro","Sonhos normais","Pesadelos","Sono agitado"].index(
                    st.session_state.get("sonhos_d","Não lembro")))

        fatores_d = st.multiselect("O que pode ter afetado o sono desta noite?",
            ["Estresse do trabalho","Discussão/conflito","Álcool","Cafeína à tarde","Refeição pesada",
             "Exercício intenso à noite","Temperatura quente","Barulho externo","Preocupações financeiras",
             "Notícias ruins","Filhosacordaram","Doença/dor","Nada especial"],
            default=st.session_state.get("fatores_d", ["Nada especial"]), key="fatores_d")

        obs_diario_d = st.text_area("Algo especial para registrar:", height=70, key="obs_diario_d",
            value=st.session_state.get("obs_diario_d",""),
            placeholder="Ex: tive reunião importante, comi pizza às 23h, tomei remédio...")

        if st.button("🤖 ANALISAR MINHA NOITE", key="btn_diario_sono", use_container_width=True):
            fats = ", ".join(fatores_d) if fatores_d else "nenhum"
            data_str = data_diario.strftime("%d/%m/%Y") if data_diario else "hoje"
            prompt = (
                f"Analise o registro de sono desta pessoa e dê feedback personalizado:\n"
                f"- Data: {data_str}\n"
                f"- Foi para cama: {hora_deitou_d} | Pegou no sono: {hora_dormiu_d}\n"
                f"- Acordou: {hora_acordou_d}\n"
                f"- Qualidade percebida: {qualidade_noite_d}/10\n"
                f"- Vezes que acordou: {vezes_acordou_d}\n"
                f"- Disposição matinal: {disposicao_manha_d}/10\n"
                f"- Sonhos: {sonhos_d}\n"
                f"- Fatores interferentes: {fats}\n"
                f"- Observações: {obs_diario_d or 'nenhuma'}\n\n"
                f"Interprete a qualidade do sono, identifique padrões ou causas prováveis e dê 3 ações para a próxima noite."
            )
            res = chamar_ia(prompt, "res_diario_sono", "Diário do Sono", f"{data_str} | qualidade {qualidade_noite_d}/10")
            if res:
                st.session_state["res_diario_sono"] = res

        if st.session_state.get("res_diario_sono"):
            st.markdown(f"<div class='card'>{st.session_state['res_diario_sono']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar registro", data=st.session_state["res_diario_sono"],
                file_name="diario_sono.txt", mime="text/plain", key="dl_diario_sono")

    # ═══════════════════════════════════════════
    # 📈 EVOLUÇÃO
    # ═══════════════════════════════════════════
    with _tab_evolucao:
        st.header("📈 Minha Evolução do Sono")
        st.markdown("Avalie como seu sono evoluiu e receba uma análise de progresso.")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            tempo_trabalhando_ev = st.selectbox("Há quanto tempo trabalha a qualidade do sono?",
                ["Estou começando agora","1–2 semanas","3–4 semanas","1–2 meses","Mais de 2 meses"],
                index=["Estou começando agora","1–2 semanas","3–4 semanas","1–2 meses","Mais de 2 meses"].index(
                    st.session_state.get("tempo_trabalhando_ev","1–2 semanas")),
                key="tempo_trabalhando_ev")
            qualidade_antes_ev = st.select_slider("Qualidade do sono ANTES (1–10):",
                options=list(range(1,11)), value=st.session_state.get("qualidade_antes_ev",3), key="qualidade_antes_ev")
            qualidade_atual_ev = st.select_slider("Qualidade do sono ATUAL (1–10):",
                options=list(range(1,11)), value=st.session_state.get("qualidade_atual_ev",6), key="qualidade_atual_ev")
        with c2:
            horas_antes_ev = st.number_input("Horas de sono ANTES (média):", min_value=1, max_value=14,
                value=st.session_state.get("horas_antes_ev",5), key="horas_antes_ev")
            horas_atual_ev = st.number_input("Horas de sono ATUAL (média):", min_value=1, max_value=14,
                value=st.session_state.get("horas_atual_ev",7), key="horas_atual_ev")
            energia_dia_ev = st.select_slider("Energia durante o dia ATUAL (1–10):",
                options=list(range(1,11)), value=st.session_state.get("energia_dia_ev",6), key="energia_dia_ev")

        melhorias_ev = st.multiselect("O que melhorou?",
            ["Pego no sono mais rápido","Acordo menos à noite","Acordo mais descansado",
             "Mais energia de dia","Humor melhor","Menos ansiedade","Memória/foco melhores",
             "Horário mais regular","Eliminei remédio para dormir","Ainda não percebi melhora"],
            default=st.session_state.get("melhorias_ev", []), key="melhorias_ev")

        desafios_ev = st.multiselect("O que ainda é desafiador?",
            ["Manter consistência nos fins de semana","Telas antes de dormir","Estresse controlando",
             "Horário irregular de trabalho","Barulho do ambiente","Acordar muito cedo",
             "Ainda demoro para pegar no sono","Ainda acordo muito à noite"],
            default=st.session_state.get("desafios_ev", []), key="desafios_ev")

        proximo_foco_ev = st.text_input("Qual quer ser seu próximo foco?",
            value=st.session_state.get("proximo_foco_ev",""),
            placeholder="Ex: eliminar o celular antes de dormir, acordar no mesmo horário...",
            key="proximo_foco_ev")

        if st.button("🤖 ANALISAR MINHA EVOLUÇÃO", key="btn_evolucao_sono", use_container_width=True):
            melh = ", ".join(melhorias_ev) if melhorias_ev else "nenhuma ainda"
            desaf = ", ".join(desafios_ev) if desafios_ev else "nenhum específico"
            prompt = (
                f"Analise a evolução do sono desta pessoa e gere um relatório de progresso:\n"
                f"- Tempo de trabalho: {tempo_trabalhando_ev}\n"
                f"- Qualidade ANTES: {qualidade_antes_ev}/10 → ATUAL: {qualidade_atual_ev}/10\n"
                f"- Horas ANTES: {horas_antes_ev}h → ATUAL: {horas_atual_ev}h\n"
                f"- Energia diurna: {energia_dia_ev}/10\n"
                f"- Melhorias percebidas: {melh}\n"
                f"- Desafios persistentes: {desaf}\n"
                f"- Próximo foco: {proximo_foco_ev or 'a definir'}\n\n"
                f"Celebre os avanços, analise os números, identifique o que está funcionando e "
                f"crie um plano de próximos passos para continuar a evolução."
            )
            res = chamar_ia(prompt, "res_evolucao_sono", "Evolução", f"{qualidade_antes_ev}→{qualidade_atual_ev}/10 | {horas_antes_ev}→{horas_atual_ev}h")
            if res:
                st.session_state["res_evolucao_sono"] = res

        if st.session_state.get("res_evolucao_sono"):
            st.markdown(f"<div class='card'>{st.session_state['res_evolucao_sono']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar relatório", data=st.session_state["res_evolucao_sono"],
                file_name="evolucao_sono.txt", mime="text/plain", key="dl_evolucao_sono")

# ── RODAPÉ ──
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;font-size:0.75em;color:#94A3B8;'>© 2026 Coach do Sono IA · Quiz Com Prêmios · Não substitui avaliação médica</div>", unsafe_allow_html=True)
