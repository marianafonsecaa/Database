from flask import Flask, render_template, redirect, url_for,request
from querys_funcoes import *
import matplotlib.pyplot as plt
import sqlite3

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    """Renderiza a página inicial e processa os formulários."""
    categories = []
    regions = []

    # Fetch categories and regions from the database
    try:
        conn = sqlite3.connect("WorldHeritage.db")
        cur = conn.cursor()

        # Query for categories
        cur.execute("SELECT DISTINCT category FROM Categoriasites")
        categories = [row[0] for row in cur.fetchall()]

        # Query for regions
        cur.execute("SELECT DISTINCT region_en FROM Regioes")
        regions = [row[0] for row in cur.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

    # Handle form submissions
    if request.method == "POST":
        if 'search_category' in request.form:
            category = request.form.get("category")
            if category:
                return redirect(url_for('search_results', category=category))
        elif 'search_region' in request.form:
            region = request.form.get("region")
            if region:
                return redirect(url_for('search_by_region', region=region))

    # Render the template with categories and regions
    return render_template("home.html", categories=categories, regions=regions)


@app.route("/results")
def search_results():
    """Renderiza a página de resultados para pesquisa por categoria."""
    category = request.args.get("category")
    results = get_sites_by_category_home(category) if category else None
    return render_template("results.html", results=results, category=category)

@app.route("/region_results")
def search_by_region():
    """Renderiza a página de resultados para pesquisa por região."""
    region = request.args.get("region")
    results = get_sites_by_region_home(region) if region else None
    return render_template("region_results.html", results=results, region=region)

@app.route("/list_sites", methods=["GET"])
def list_sites():
    """Lista todos os sítios da base de dados."""
    try:
        conn = sqlite3.connect("WorldHeritage.db")
        cur = conn.cursor()
        cur.execute("SELECT name_en FROM Sitios")
        sites = [row[0] for row in cur.fetchall()]
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {e}")
        sites = []
    finally:
        if conn:
            conn.close()
    return render_template("list_sites.html", sites=sites)

@app.route("/site_details/<site_name>", methods=["GET"])
def site_details(site_name):
    """Exibe os detalhes de um sítio específico."""
    try:
        conn = sqlite3.connect("WorldHeritage.db")
        cur = conn.cursor()
        query = """
            SELECT sitioid as ID, 
            short_description_en as Descrição, 
            justification_en as Justificação, 
            date_inscribed as 'Data de Inscrição',
            secondary_dates as 'Datas de revisão',
            danger as 'Em perigo',
            date_end as 'Data de exclusão da lista de sítios em perigo',
            danger_list as 'Data de entrada e possível saída da lista de sítios em perigo',
            longitude as 'Longitude',
            latitude as 'Latitude',
            categoriasiteid as 'Categoria',
            area_hectares as 'Área'
            FROM Sitios 
            WHERE name_en = ?
        """
        cur.execute(query, (site_name,))
        site_details = cur.fetchone()
        column_names = [description[0] for description in cur.description]
        # Combine colunas e valores em pares
        details = list(zip(column_names, site_details)) if site_details else None
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {e}")
        details = None
    finally:
        if conn:
            conn.close()
    return render_template("site_details.html", site_name=site_name, details=details)


@app.route("/q1")
def question1():
    """Render the table for Q1 with a pie chart."""
    try:
        data = get_sites_by_category()
        categories = [row[0] for row in data]
        counts = [row[1] for row in data]

        # Generate the pie chart
        plot_path = os.path.join(app.static_folder, "q1_pie_chart.png")
        plt.figure(figsize=(8, 8))
        plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=140, colors=['#ff9999', '#66b3ff', '#99ff99'])
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        return render_template("query1.html", data=data, plot_url=url_for('static', filename='q1_pie_chart.png'))
    except Exception as e:
        app.logger.error(f"Error generating pie chart: {e}")
        return "An error occurred while processing your request.", 500



@app.route("/q2")
def question2():
    """Render the table for Q2."""
    data = get_sites_by_region()
    return render_template("query2.html", data=data)

@app.route("/q3")
def question3():
    """Render the table for Q3."""
    data = get_top_states_with_sites()
    return render_template("query3.html", data=data)

@app.route("/q4")
def question4():
    """Render the table for Q4."""
    data = get_site_with_max_area()
    return render_template("query4.html", data=data)

@app.route("/q5")
def question5():
    """Render the table for criteria dominance analysis."""
    data = analyze_criteria_dominance()  # Chama a função para obter os dados
    mismatch_count = sum(1 for row in data if row[-1] == 'Mismatch')  # Calcula os Mismatch
    return render_template("query5.html", data=data, mismatch_count=mismatch_count)

@app.route("/q6")
def question6():
    """Render the table for Q6."""
    data = get_sites_with_date_end()
    return render_template("query6.html", data=data)

@app.route("/q7")
def question7():
    """Render the table for Q7."""
    data = get_sites_no_end_date()
    return render_template("query7.html", data=data)

@app.route("/q8")
def question8():
    """Render the table for Q8."""
    data = count_sites_by_region_and_category()
    return render_template("query8.html", data=data)

@app.route("/q9")
def question9():
    """Render the table for Q9."""
    data = get_sites_in_danger_by_category()
    return render_template("query9.html", data=data)

@app.route("/q10")
def question10():
    """Render the table for Q10."""
    data = get_transboundary_sites_with_multiple_states()
    return render_template("query10.html", data=data)

@app.route("/q11")
def question11():
    """Render the table and bar chart for the number of sites inscribed per year."""
    try:
        # Fetch data from the database
        data = get_inscribed_sites_per_year()
        if not data:
            raise ValueError("No data available for the inscribed sites per year.")

        # Extract data for plotting
        years = [row[0] for row in data]  # X-axis (years)
        counts = [row[1] for row in data]  # Y-axis (number of sites)

        # Path to save the plot
        plot_path = os.path.join(app.static_folder, "sites_per_year.png")

        # Generate the bar chart
        plt.figure(figsize=(12, 6))
        plt.bar(years, counts, color='skyblue', edgecolor='black')
        plt.xlabel("Ano")
        plt.ylabel("Número de sítios")
        plt.title("Número de sítios inscritos por ano")
        plt.xticks(ticks=years, rotation=45)
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        # Render the results
        return render_template("query11.html", data=data, plot_url=url_for('static', filename='sites_per_year.png'))
    except Exception as e:
        app.logger.error(f"Error in question11 route: {e}")
        return "An error occurred while generating the chart. Please try again later.", 500


@app.route("/q12")
def question12():
    """Render the table for Q12."""
    data = get_secondary_dates_count()
    return render_template("query12.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)

