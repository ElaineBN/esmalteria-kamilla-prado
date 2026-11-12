import sqlite3
import matplotlib.pyplot as plt
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Esmalteria Kamilla Prado", page_icon="💅", layout="centered"
)


# Inicialização e Atualização Automática do Banco de Dados SQLite
def inicializar_banco():
  conn = sqlite3.connect("esmalteria.db")
  cursor = conn.cursor()

  cursor.execute(
      "CREATE TABLE IF NOT EXISTS servicos (id INTEGER PRIMARY KEY"
      " AUTOINCREMENT, nome TEXT NOT NULL, valor REAL NOT NULL)"
  )
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS despesas (id INTEGER PRIMARY KEY"
      " AUTOINCREMENT, descricao TEXT NOT NULL, tipo TEXT NOT NULL, valor REAL"
      " NOT NULL)"
  )
  cursor.execute("PRAGMA table_info(despesas)")
  colunas = [col[1] for col in cursor.fetchall()]
  if "data" not in colunas:
    cursor.execute("ALTER TABLE despesas ADD COLUMN data TEXT DEFAULT ''")

  cursor.execute(
      "CREATE TABLE IF NOT EXISTS receitas (id INTEGER PRIMARY KEY"
      " AUTOINCREMENT, servico TEXT NOT NULL, valor REAL NOT NULL, data TEXT NOT"
      " NULL)"
  )

  conn.commit()
  conn.close()


inicializar_banco()

st.title("💅 Esmalteria Kamilla Prado")
st.subheader("Controle Financeiro e Gestão")

# Menu lateral de navegação
menu = st.sidebar.selectbox(
    "Menu de Navegação",
    ["Serviços", "Despesas", "Receitas", "Histórico por Período", "Balanço & Gráficos"],
)

# ================= 1. SERVIÇOS (RF01 e RF07) =================
if menu == "Serviços":
  st.header("Gerenciar Serviços")
  st.info(
      "Para alterar ou excluir, informe o ID. Ao digitar um ID válido, os campos"
      " preenchem sozinhos."
  )

  id_s_input = st.text_input(
      "ID do Serviço (Para Alterar ou Excluir):", key="input_id_serv"
  )

  s_nome, s_valor = "", 0.0
  if id_s_input.isdigit():
    conn = sqlite3.connect("esmalteria.db")
    res = conn.execute(
        "SELECT nome, valor FROM servicos WHERE id = ?", (id_s_input,)
    ).fetchone()
    conn.close()
    if res:
      s_nome, s_valor = res[0], res[1]

  with st.form("form_servico"):
    nome = st.text_input("Nome do Serviço:", value=s_nome)
    valor = st.number_input(
        "Valor Padrão (R$):", min_value=0.0, value=float(s_valor), format="%.2f"
    )

    col1, col2, col3 = st.columns(3)
    submitted = col1.form_submit_button("Cadastrar Novo")
    updated = col2.form_submit_button("Salvar Alteração")
    deleted = col3.form_submit_button("Excluir por ID")

  if submitted:
    if nome and valor > 0:
      conn = sqlite3.connect("esmalteria.db")
      conn.execute(
          "INSERT INTO servicos (nome, valor) VALUES (?, ?)", (nome, valor)
      )
      conn.commit()
      conn.close()
      st.success("Serviço cadastrado com sucesso!")
      st.rerun()
    else:
      st.error("Preencha o nome e um valor válido.")

  if updated:
    if id_s_input and nome:
      conn = sqlite3.connect("esmalteria.db")
      conn.execute(
          "UPDATE servicos SET nome = ?, valor = ? WHERE id = ?",
          (nome, valor, id_s_input),
      )
      conn.commit()
      conn.close()
      st.success(f"Serviço ID {id_s_input} alterado com sucesso!")
      st.rerun()
    else:
      st.error("Informe um ID válido e o nome para alterar.")

  if deleted:
    if id_s_input:
      conn = sqlite3.connect("esmalteria.db")
      conn.execute("DELETE FROM servicos WHERE id = ?", (id_s_input,))
      conn.commit()
      conn.close()
      st.success(f"Serviço ID {id_s_input} excluído com sucesso!")
      st.rerun()
    else:
      st.error("Informe o ID para excluir.")

  st.divider()
  st.subheader("Serviços Cadastrados")
  conn = sqlite3.connect("esmalteria.db")
  servicos = conn.execute("SELECT * FROM servicos").fetchall()
  conn.close()

  if servicos:
    for s in servicos:
      st.write(
          f"**ID:** {s[0]} | **{s[1]}** - R$ {s[2]:.2f}"
      )
  else:
    st.info("Nenhum serviço cadastrado ainda.")

# ================= 2. DESPESAS (RF02 e RF07) =================
elif menu == "Despesas":
  st.header("Gerenciar Despesas")
  st.info(
      "Para alterar ou excluir, informe o ID. Ao digitar um ID válido, os campos"
      " preenchem sozinhos."
  )

  id_d_input = st.text_input(
      "ID da Despesa (Para Alterar ou Excluir):", key="input_id_desp"
  )

  d_desc, d_tipo, d_valor, d_data = "", "Fixa", 0.0, ""
  if id_d_input.isdigit():
    conn = sqlite3.connect("esmalteria.db")
    res = conn.execute(
        "SELECT descricao, tipo, valor, data FROM despesas WHERE id = ?",
        (id_d_input,),
    ).fetchone()
    conn.close()
    if res:
      d_desc, d_tipo, d_valor, d_data = res[0], res[1], res[2], res[3]

  with st.form("form_despesa"):
    desc = st.text_input("Descrição (Ex: Aluguel, Esmaltes):", value=d_desc)
    tipo_idx = 0 if d_tipo == "Fixa" else 1
    tipo = st.selectbox(
        "Tipo de Despesa:", ["Fixa", "Variável"], index=tipo_idx
    )
    valor_d = st.number_input(
        "Valor da Despesa (R$):",
        min_value=0.0,
        value=float(d_valor),
        format="%.2f",
    )
    data_d = st.text_input(
        "Data da Despesa (DD/MM/AAAA):",
        value=d_data,
        placeholder="Ex: 28/10/2026",
    )

    col1, col2, col3 = st.columns(3)
    submitted_d = col1.form_submit_button("Cadastrar Nova")
    updated_d = col2.form_submit_button("Salvar Alteração")
    deleted_d = col3.form_submit_button("Excluir por ID")

  if submitted_d:
    if desc and data_d and valor_d > 0:
      conn = sqlite3.connect("esmalteria.db")
      conn.execute(
          "INSERT INTO despesas (descricao, tipo, valor, data) VALUES (?, ?, ?,"
          " ?)",
          (desc, tipo, valor_d, data_d),
      )
      conn.commit()
      conn.close()
      st.success("Despesa cadastrada com sucesso!")
      st.rerun()
    else:
      st.error("Preencha a descrição, a data e o valor.")

  if updated_d:
    if id_d_input and desc:
      conn = sqlite3.connect("esmalteria.db")
      conn.execute(
          "UPDATE despesas SET descricao = ?, tipo = ?, valor = ?, data = ? WHERE"
          " id = ?",
          (desc, tipo, valor_d, data_d, id_d_input),
      )
      conn.commit()
      conn.close()
      st.success(f"Despesa ID {id_d_input} alterada com sucesso!")
      st.rerun()
    else:
      st.error("Informe um ID válido e a descrição.")

  if deleted_d:
    if id_d_input:
      conn = sqlite3.connect("esmalteria.db")
      conn.execute("DELETE FROM despesas WHERE id = ?", (id_d_input,))
      conn.commit()
      conn.close()
      st.success(f"Despesa ID {id_d_input} excluída com sucesso!")
      st.rerun()
    else:
      st.error("Informe o ID para excluir.")

  st.divider()
  st.subheader("Despesas Cadastradas")
  conn = sqlite3.connect("esmalteria.db")
  despesas = conn.execute("SELECT * FROM despesas").fetchall()
  conn.close()

  if despesas:
    for d in despesas:
      data_exibicao = d[4] if len(d) > 4 and d[4] else "Não informada"
      st.write(
          f"**ID:** {d[0]} | **Data:** {data_exibicao} | **[{d[2]}]** {d[1]} -"
          f" R$ {d[3]:.2f}"
      )
  else:
    st.info("Nenhuma despesa cadastrada.")

# ================= 3. RECEITAS (RF03 e RF07) =================
elif menu == "Receitas":
  st.header("Registrar Atendimentos / Receitas")
  st.info(
      "Para alterar ou excluir, informe o ID. Ao digitar um ID válido, os campos"
      " preenchem sozinhos."
  )

  conn = sqlite3.connect("esmalteria.db")
  servicos_cadastrados = conn.execute("SELECT nome, valor FROM servicos").fetchall()
  conn.close()

  if not servicos_cadastrados:
    st.warning(
        "⚠️ Cadastre pelo menos um serviço na aba 'Serviços' antes de registrar"
        " receitas!"
    )
  else:
    dict_servicos = {s[0]: s[1] for s in servicos_cadastrados}
    lista_nomes_servicos = list(dict_servicos.keys())

    id_r_input = st.text_input(
        "ID da Receita (Para Alterar ou Excluir):", key="input_id_rec"
    )

    r_servico, r_valor, r_data = lista_nomes_servicos[
        0
    ], dict_servicos.get(lista_nomes_servicos[0], 0.0), ""
    if id_r_input.isdigit():
      conn = sqlite3.connect("esmalteria.db")
      res = conn.execute(
          "SELECT servico, valor, data FROM receitas WHERE id = ?",
          (id_r_input,),
      ).fetchone()
      conn.close()
      if res:
        r_servico, r_valor, r_data = res[0], res[1], res[2]
        if r_servico not in lista_nomes_servicos:
          lista_nomes_servicos.insert(0, r_servico)

    serv_idx = (
        lista_nomes_servicos.index(r_servico)
        if r_servico in lista_nomes_servicos
        else 0
    )

    with st.form("form_receita"):
      servico_selecionado = st.selectbox(
          "Selecione o Serviço:", lista_nomes_servicos, index=serv_idx
      )
      valor_rec = st.number_input(
          "Valor Cobrado (R$) - Ajuste em caso de desconto:",
          min_value=0.0,
          value=float(r_valor),
          format="%.2f",
      )
      data_rec = st.text_input(
          "Data (DD/MM/AAAA):",
          value=r_data,
          placeholder="Ex: 28/10/2026",
      )

      col1, col2, col3 = st.columns(3)
      submitted_r = col1.form_submit_button("Registrar Nova")
      updated_r = col2.form_submit_button("Salvar Alteração")
      deleted_r = col3.form_submit_button("Excluir por ID")

    if submitted_r:
      if servico_selecionado and data_rec and valor_rec >= 0:
        conn = sqlite3.connect("esmalteria.db")
        conn.execute(
            "INSERT INTO receitas (servico, valor, data) VALUES (?, ?, ?)",
            (servico_selecionado, valor_rec, data_rec),
        )
        conn.commit()
        conn.close()
        st.success("Receita registrada com sucesso!")
        st.rerun()
      else:
        st.error("Preencha todos os campos corretamente.")

    if updated_r:
      if id_r_input and servico_selecionado:
        conn = sqlite3.connect("esmalteria.db")
        conn.execute(
            "UPDATE receitas SET servico = ?, valor = ?, data = ? WHERE id = ?",
            (servico_selecionado, valor_rec, data_rec, id_r_input),
        )
        conn.commit()
        conn.close()
        st.success(f"Receita ID {id_r_input} alterada com sucesso!")
        st.rerun()
      else:
        st.error("Informe um ID válido para alterar.")

    if deleted_r:
      if id_r_input:
        conn = sqlite3.connect("esmalteria.db")
        conn.execute("DELETE FROM receitas WHERE id = ?", (id_r_input,))
        conn.commit()
        conn.close()
        st.success(f"Receita ID {id_r_input} excluída com sucesso!")
        st.rerun()
      else:
        st.error("Informe o ID para excluir.")

  st.divider()
  st.subheader("Receitas Registradas")
  conn = sqlite3.connect("esmalteria.db")
  receitas = conn.execute("SELECT * FROM receitas").fetchall()
  conn.close()

  if receitas:
    for r in receitas:
      st.write(
          f"**ID:** {r[0]} | **Data:** {r[3]} | **Serviço:** {r[1]} - **Valor"
          f" Cobrado:** R$ {r[2]:.2f}"
      )
  else:
    st.info("Nenhuma receita registrada.")

# ================= 4. HISTÓRICO POR PERÍODO (RF06) =================
elif menu == "Histórico por Período":
  st.header("Consulta de Histórico Financeiro")
  st.write("Filtre os registros de receitas por período ou data específica[cite: 8].")

  tipo_filtro = st.radio(
      "Selecione o tipo de pesquisa:",
      [
          "Todos os registros",
          "Data específica (Ex: 28/10/2026)",
          "Mês e Ano (Ex: 10/2026)",
          "Apenas Mês (Ex: 10) / Apenas Ano (Ex: 2026)",
      ],
  )

  termo_busca = ""
  query_sql = "SELECT * FROM receitas WHERE data LIKE ?"
  parametro_sql = ("",)

  if tipo_filtro == "Todos os registros":
    query_sql = "SELECT * FROM receitas"
  elif tipo_filtro == "Data específica (Ex: 28/10/2026)":
    termo_busca = st.text_input(
        "Digite a data (DD/MM/AAAA):", placeholder="Ex: 28/10/2026"
    )
    parametro_sql = (f"%{termo_busca}%",)
  elif tipo_filtro == "Mês e Ano (Ex: 10/2026)":
    termo_busca = st.text_input(
        "Digite o mês e ano (MM/AAAA):", placeholder="Ex: 10/2026"
    )
    parametro_sql = (f"%/{termo_busca}%",)
  elif tipo_filtro == "Apenas Mês (Ex: 10) / Apenas Ano (Ex: 2026)":
    termo_busca = st.text_input(
        "Digite o mês (ex: 11) ou ano (ex: 2026):", placeholder="Ex: 11"
    )
    if len(termo_busca.strip()) <= 2 and termo_busca.strip().isdigit():
      parametro_sql = (f"%/{termo_busca.strip()}/%",)
    else:
      parametro_sql = (f"%{termo_busca}%",)

  conn = sqlite3.connect("esmalteria.db")
  if tipo_filtro == "Todos os registros":
    resultados = conn.execute(query_sql).fetchall()
  else:
    cursor = conn.cursor()
    cursor.execute(query_sql, parametro_sql)
    resultados = cursor.fetchall()
  conn.close()

  st.divider()
  if resultados:
    st.success(f"Encontrados {len(resultados)} registro(s):")
    for row in resultados:
      st.info(f"Data: {row[3]} | Serviço: {row[1]} | Valor: R$ {row[2]:.2f}")
  else:
    st.warning("Nenhum registro encontrado para este critério de busca.")

# ================= 5. BALANÇO E GRÁFICOS (RF04 / RNF04) =================
elif menu == "Balanço & Gráficos":
  st.header("Balanço Financeiro e Painel Gerencial")

  conn = sqlite3.connect("esmalteria.db")
  cur = conn.cursor()
  receitas_raw = cur.execute("SELECT valor, data FROM receitas").fetchall()
  despesas_raw = cur.execute("SELECT tipo, valor, data FROM despesas").fetchall()
  conn.close()

  st.divider()
  st.subheader("🔍 Comparativo e Filtro de Períodos")

  # Extrai todos os meses/anos únicos existentes nos cadastros
  meses_disponiveis = set()
  for _, data in receitas_raw:
    if data and len(data) >= 10:
      meses_disponiveis.add(data[3:])
  for _, _, data in despesas_raw:
    if data and len(data) >= 10:
      meses_disponiveis.add(data[3:])

  lista_meses_ordenada = sorted(list(meses_disponiveis))

  # Seletor múltiplo para o usuário comparar períodos diferentes (ex: Outubro/2026 e Outubro/2027)
  meses_selecionados = st.multiselect(
      "Selecione os meses/anos que deseja comparar nos gráficos:",
      options=lista_meses_ordenada,
      default=lista_meses_ordenada  # Por padrão seleciona todos
  )

  # Aplica o filtro com base na escolha múltipla
  rec_filtrado = []
  for val, data in receitas_raw:
    if data and len(data) >= 10:
      if not meses_selecionados or data[3:] in meses_selecionados:
        rec_filtrado.append((val, data))

  desp_filtrado = []
  for tipo_d, val, data in despesas_raw:
    if data and len(data) >= 10:
      if not meses_selecionados or data[3:] in meses_selecionados:
        desp_filtrado.append((tipo_d, val, data))

  tot_rec_f = sum([r[0] for r in rec_filtrado])
  tot_esp_f = sum([d[1] for d in desp_filtrado])
  lucro_f = tot_rec_f - tot_esp_f

  col1, col2, col3 = st.columns(3)
  col1.metric("Receitas (Seleção)", f"R$ {tot_rec_f:.2f}")
  col2.metric("Despesas (Seleção)", f"R$ {tot_esp_f:.2f}")
  col3.metric(
      "Lucro Líquido (Seleção)", f"R$ {lucro_f:.2f}", delta=f"R$ {lucro_f:.2f}"
  )

  st.divider()
  st.subheader("📊 Painel de Análises Comparativas")

  if not rec_filtrado and not desp_filtrado:
    st.info("Selecione pelo menos um período acima ou registe dados para visualizar os gráficos.")
  else:
    meses_dict = {}

    for val, data in rec_filtrado:
      mes_ano = data[3:]
      if mes_ano not in meses_dict:
        meses_dict[mes_ano] = {"rec": 0.0, "esp": 0.0}
      meses_dict[mes_ano]["rec"] += val

    for tipo_d, val, data in desp_filtrado:
      mes_ano = data[3:]
      if mes_ano not in meses_dict:
        meses_dict[mes_ano] = {"rec": 0.0, "esp": 0.0}
      meses_dict[mes_ano]["esp"] += val

    meses_ordenados = sorted(list(meses_dict.keys()))

    if meses_ordenados:
      # 1. Gráfico de Colunas Agrupadas (Comparativo)
      st.markdown("### 1. Faturamento vs. Despesas (Comparativo)")
      st.write("Compara o total de entradas e saídas lado a lado para os períodos escolhidos.")

      fig1, ax1 = plt.subplots(figsize=(7, 4.2))
      x = range(len(meses_ordenados))
      width = 0.35

      rec_valores = [meses_dict[m]["rec"] for m in meses_ordenados]
      esp_valores = [meses_dict[m]["esp"] for m in meses_ordenados]

      barras_rec = ax1.bar(
          [i - width / 2 for i in x],
          rec_valores,
          width,
          label="Receitas",
          color="#2ecc71",
      )
      barras_esp = ax1.bar(
          [i + width / 2 for i in x],
          esp_valores,
          width,
          label="Despesas",
          color="#e74c3c",
      )

      for barra in barras_rec:
        altura = barra.get_height()
        ax1.annotate(
            f"R$ {altura:.2f}",
            xy=(barra.get_x() + barra.get_width() / 2, altura),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )

      for barra in barras_esp:
        altura = barra.get_height()
        ax1.annotate(
            f"R$ {altura:.2f}",
            xy=(barra.get_x() + barra.get_width() / 2, altura),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )

      max_val = (
          max(max(rec_valores), max(esp_valores))
          if (rec_valores and esp_valores)
          else 100
      )
      ax1.set_ylim(0, max_val * 1.25 if max_val > 0 else 100)

      ax1.set_ylabel("R$")
      ax1.set_title("Comparativo Mensal/Anual: Receitas vs Despesas")
      ax1.set_xticks(list(x))
      ax1.set_xticklabels(meses_ordenados)
      ax1.legend()
      ax1.grid(axis="y", linestyle="--", alpha=0.5)
      st.pyplot(fig1)

      # 2. Gráfico de Linha de Tendência (Evolução dos Períodos Selecionados)
      st.markdown("### 2. Evolução do Lucro Líquido (Tendência)")
      st.write("Mostra a curva de lucro para os períodos específicos selecionados.")

      lucro_valores = [
          meses_dict[m]["rec"] - meses_dict[m]["esp"] for m in meses_ordenados
      ]

      fig2, ax2 = plt.subplots(figsize=(7, 3.8))
      ax2.plot(
          meses_ordenados,
      lucro_valores,
          marker="o",
          color="#3498db",
          linewidth=2.5,
          markersize=8,
      )
      ax2.fill_between(
          meses_ordenados, lucro_valores, color="#3498db", alpha=0.15
      )

      for i, txt in enumerate(lucro_valores):
        ax2.annotate(
            f"R$ {txt:.2f}",
            (meses_ordenados[i], lucro_valores[i]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=9,
            fontweight="bold",
            color="#2980b9",
        )

      if lucro_valores:
        min_lucro = min(lucro_valores)
        max_lucro = max(lucro_valores)
        margem = (
            abs(max_lucro - min_lucro) * 0.3
            if max_lucro != min_lucro
            else abs(min_lucro) * 0.3 + 50
        )
        ax2.set_ylim(min_lucro - margem - 20, max_lucro + margem + 20)

      ax2.set_ylabel("Lucro Líquido (R$)")
      ax2.set_title("Curva de Tendência do Lucro")
      ax2.grid(True, linestyle="--", alpha=0.5)
      st.pyplot(fig2)

    # 3. Gráfico de Rosca (Proporção de Despesas da Seleção)
    st.markdown("### 3. Distribuição das Despesas (Fixas vs. Variáveis)")
    st.write(
        "Analisa visualmente o peso de cada categoria de custo para os períodos selecionados."
    )

    if desp_filtrado:
      tipos_despesa = {}
      for tipo, val, _ in desp_filtrado:
        tipos_despesa[tipo] = tipos_despesa.get(tipo, 0.0) + val

      labels = list(tipos_despesa.keys())
      tamanhos = list(tipos_despesa.values())
      cores_rosca = ["#e67e22", "#9b59b6", "#f1c40f"]

      fig3, ax3 = plt.subplots(figsize=(6, 4))
      wedges, texts, autotexts = ax3.pie(
          tamanhos,
          labels=labels,
          autopct="%1.1f%%",
          startangle=90,
          colors=cores_rosca[: len(labels)],
          wedgeprops=dict(width=0.4, edgecolor="w"),
      )
      plt.setp(autotexts, size=10, weight="bold")
      ax3.set_title("Proporção de Gastos por Categoria")
      st.pyplot(fig3)
    else:
      st.info("Nenhuma despesa registada para os períodos selecionados.")