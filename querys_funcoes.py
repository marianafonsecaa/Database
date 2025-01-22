import sqlite3
import sys
import os

# Fix for Unicode display issues on Windows
if os.name == 'nt':  # Check if the OS is Windows
    import locale
    locale.setlocale(locale.LC_ALL, '')
    sys.stdout.reconfigure(encoding='utf-8')

def get_sites_by_category_home(category, db_path="WorldHeritage.db"):
    """Fetch sites by category from the database."""
    query = """
        SELECT Sitios.name_en
        FROM Sitios NATURAL JOIN Categoriasites 
        WHERE Categoriasites.category LIKE ?
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Execute the query
        cur.execute(query, (f"%{category}%",))
        results = cur.fetchall()

        # Convert the result to a simple list of site names
        return [row[0] for row in results]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()



def get_sites_by_region_home(region, db_path="WorldHeritage.db"):
    """Fetch sites by region from the database."""
    query = """
        SELECT Sitios.name_en as Sítio
        FROM Sitios 
        NATURAL JOIN Sitios_estados 
        NATURAL JOIN Estados 
        NATURAL JOIN Regioes
        WHERE region_en LIKE ?
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Execute the query
        cur.execute(query, (f"%{region}%",))
        results = cur.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_sites_by_category(db_path="WorldHeritage.db"):
    """Fetch the number of sites for each category."""
    query = """
    SELECT categoriasites.category AS Categoria, COUNT(*) AS num
    FROM Sitios natural join Categoriasites
    GROUP BY Sitios.categoriasiteid
    ORDER BY COUNT(*) DESC;
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Execute the query
        cur.execute(query)
        results = cur.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_sites_by_region(db_path="WorldHeritage.db"):
    """
    Fetch the total number of distinct sites for each region.
    """
    query = """
    SELECT 
        r.region_en AS regiao,
        COUNT(DISTINCT se.sitioid) AS total_sitios
    FROM 
        Regioes r
    JOIN 
        Estados e ON r.regiaoid = e.regiaoid
    JOIN 
        Sitios_Estados se ON e.estadoid = se.estadoid
    JOIN 
        Sitios s ON se.sitioid = s.sitioid
    GROUP BY 
        r.region_en
    ORDER BY 
        total_sitios DESC;
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        return results  # Return the results as a list of tuples
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_top_states_with_sites(db_path="WorldHeritage.db", limit=10):
    """
    Fetch the top states with the highest number of unique sites.
    """
    query = f"""
    WITH RECURSIVE SplitEstados AS (
        -- Extract states separated by commas
        SELECT 
            se.sitioid,
            TRIM(SUBSTR(e.states_name_en, 1, INSTR(e.states_name_en || ',', ',') - 1)) AS estado_separado,
            SUBSTR(e.states_name_en, INSTR(e.states_name_en || ',', ',') + 1) AS resto
        FROM 
            Estados e
        JOIN 
            Sitios_Estados se ON e.estadoid = se.estadoid

        UNION ALL

        -- Process the next state in the list
        SELECT 
            sitioid,
            TRIM(SUBSTR(resto, 1, INSTR(resto || ',', ',') - 1)) AS estado_separado,
            SUBSTR(resto, INSTR(resto || ',', ',') + 1) AS resto
        FROM 
            SplitEstados
        WHERE 
            resto <> ''
    )
    SELECT 
        estado_separado AS estado,
        COUNT(DISTINCT sitioid) AS total_sitios
    FROM 
        SplitEstados
    GROUP BY 
        estado_separado
    ORDER BY 
        total_sitios DESC
    LIMIT {limit};
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        return results  # Return the results as a list of tuples
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_site_with_max_area(db_path="WorldHeritage.db"):
    """
    Fetch the site with the largest area in hectares.
    """
    query = """
    SELECT 
        name_en, 
        area_hectares
    FROM 
        Sitios
    WHERE 
        area_hectares = (SELECT MAX(area_hectares) FROM Sitios);
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        result = cursor.fetchall()

        return result  # Return the result as a list of tuples
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

import sqlite3

def analyze_criteria_dominance(db_path="WorldHeritage.db"):
    """
    Analyze criteria dominance for each site and compare it to the assigned category.
    Returns a list of tuples for rendering in the HTML template.
    """
    query = '''
    WITH CriteriaCounts AS (
        SELECT
            s.name_en,
            v.sitioid,
            c.categoriaid AS criteria_type,
            COUNT(v.valor) AS criteria_count
        FROM Valores v
        JOIN Criterios c ON v.criterioid = c.criterioid
        JOIN Sitios s ON s.sitioid = v.sitioid
        WHERE v.valor = 1
        GROUP BY v.sitioid, c.categoriaid
    ),
    DominantCategory AS (
        SELECT
            name_en,
            sitioid,
            MAX(CASE WHEN criteria_type = 'C' THEN criteria_count ELSE 0 END) AS cultural_count,
            MAX(CASE WHEN criteria_type = 'N' THEN criteria_count ELSE 0 END) AS natural_count,
            CASE
                WHEN MAX(CASE WHEN criteria_type = 'C' THEN criteria_count ELSE 0 END) >
                     MAX(CASE WHEN criteria_type = 'N' THEN criteria_count ELSE 0 END) THEN 'C'
                WHEN MAX(CASE WHEN criteria_type = 'C' THEN criteria_count ELSE 0 END) <
                     MAX(CASE WHEN criteria_type = 'N' THEN criteria_count ELSE 0 END) THEN 'N'
                ELSE 'C/N'
            END AS dominant_category
        FROM CriteriaCounts
        GROUP BY sitioid
    )
    SELECT
        d.name_en,
        d.cultural_count,
        d.natural_count,
        d.dominant_category,
        cs.category AS assigned_category,
        CASE
            WHEN (d.dominant_category = 'C' AND cs.category = 'Cultural') OR 
                 (d.dominant_category = 'N' AND cs.category = 'Natural') OR
                 (d.dominant_category = 'C/N' AND cs.category = 'Mixed')
            THEN 'Match'
            ELSE 'Mismatch'
        END AS category_consistency
    FROM DominantCategory d
    JOIN Categoriasites cs ON d.dominant_category = cs.categoriasiteid
    ORDER BY sitioid;
    '''
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_sites_with_date_end(db_path="WorldHeritage.db"):
    """
    Fetches the name, date_inscribed, date_end, and the number of years inscribed
    (date_end - date_inscribed) for sites where date_end is not NULL.

    Parameters:
        db_path (str): Path to the SQLite database file.

    Returns:
        list of tuples: Each tuple contains (name_en, date_inscribed, date_end, num_years).
    """
    sql_query = """
    SELECT 
        name_en, 
        CAST(date_inscribed AS INTEGER) AS date_inscribed, 
        CAST(date_end AS INTEGER) AS date_end, 
        CAST(date_end AS INTEGER) - CAST(date_inscribed AS INTEGER) AS 'Nº de anos incritos'
    FROM sitios
    WHERE date_end IS NOT NULL;
    """

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(sql_query)
        results = cursor.fetchall()

        return results  # Return the query results

    except sqlite3.Error as e:
        print("An error occurred:", e)
        return []

    finally:
        # Ensure the connection is closed
        conn.close()

def get_sites_no_end_date(db_path="WorldHeritage.db"):
    """
    Fetch the first 10 sites where the 'date_end' is NULL, ordered by 'date_inscribed' in ascending order.
    """
    query = """
    SELECT 
        s.sitioid,
        s.name_en,
        s.date_inscribed
    FROM 
        Sitios s
    WHERE 
        s.date_end IS NULL
    ORDER BY 
        s.date_inscribed ASC
    LIMIT 10
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def count_sites_by_region_and_category(db_path="WorldHeritage.db"):
    """
    Count the number of World Heritage Sites by region and category.
    """
    query = """
    WITH ContagemPorRegiao AS (
        SELECT 
            r.region_en AS regiao,
            cs.category AS categoria,
            COUNT(DISTINCT s.sitioid) AS total_sitios
        FROM 
            Regioes r
        JOIN 
            Estados e ON r.regiaoid = e.regiaoid
        JOIN 
            Sitios_Estados se ON e.estadoid = se.estadoid
        JOIN 
            Sitios s ON se.sitioid = s.sitioid
        JOIN 
            Categoriasites cs ON s.categoriasiteid = cs.categoriasiteid
        GROUP BY 
            r.region_en, cs.category
    ),
    TotaisPorRegiao AS (
        SELECT 
            regiao,
            SUM(CASE WHEN categoria = 'Natural' THEN total_sitios ELSE 0 END) AS total_natural,
            SUM(CASE WHEN categoria = 'Cultural' THEN total_sitios ELSE 0 END) AS total_cultural,
            SUM(CASE WHEN categoria = 'Mixed' THEN total_sitios ELSE 0 END) AS total_mixed
        FROM 
            ContagemPorRegiao
        GROUP BY 
            regiao
    )
    SELECT 
        regiao,
        total_natural,
        total_cultural,
        total_mixed
    FROM 
        TotaisPorRegiao
    ORDER BY 
        regiao
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_sites_in_danger_by_category(db_path="WorldHeritage.db"):
    """
    Fetch the number of sites in danger grouped by their category.
    """
    query = """
    SELECT cs.category, COUNT(s.sitioid) AS total_em_perigo
    FROM Sitios s
    JOIN Categoriasites cs ON s.categoriasiteid = cs.categoriasiteid
    WHERE s.danger = '1'
    GROUP BY cs.category;
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_transboundary_sites_with_multiple_states(db_path="WorldHeritage.db"):
    """
    Fetch the sites that belong to more than one state and list the states for each site.
    """
    query = r"""
    WITH RECURSIVE SplitEstados AS (
        -- Pega os estados separados por vírgulas
        SELECT 
            e.sitioid,
            TRIM(SUBSTR(e.states_name_en, 1, INSTR(e.states_name_en || ',', ',') - 1)) AS estado_separado,
            SUBSTR(e.states_name_en, INSTR(e.states_name_en || ',', ',') + 1) AS resto
        FROM 
            Estados e 
        JOIN 
            Sitios_Estados se ON e.estadoid = se.estadoid

        UNION ALL

        -- Processa o próximo estado na lista
        SELECT 
            sitioid,
            TRIM(SUBSTR(resto, 1, INSTR(resto || ',', ',') - 1)) AS estado_separado,
            SUBSTR(resto, INSTR(resto || ',', ',') + 1) AS resto
        FROM 
            SplitEstados
        WHERE 
            resto <> ''
    ),
    SitiosComMaisDeUmEstado AS (
        -- Conta o número de estados por sítio
        SELECT 
            sitioid,
            COUNT(DISTINCT estado_separado) AS total_estados
        FROM 
            SplitEstados
        GROUP BY 
            sitioid
        HAVING 
            total_estados > 1 -- Apenas sítios com mais de um estado
    )
    SELECT 
        s.name_en AS nome_sitio,
        COUNT(DISTINCT se.estado_separado) AS numero_estados,
        GROUP_CONCAT(DISTINCT se.estado_separado) AS estados
    FROM 
        SplitEstados se
    JOIN 
        SitiosComMaisDeUmEstado scmde ON se.sitioid = scmde.sitioid
    JOIN 
        Sitios s ON se.sitioid = s.sitioid
    GROUP BY 
        s.name_en
    ORDER BY 
        numero_estados DESC;
    """
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_inscribed_sites_per_year(db_path="WorldHeritage.db"):
    """
    Fetch the number of sites inscribed by year from the database.
    """
    sql_query = """
    SELECT date_inscribed AS 'Data de inscrição', 
           COUNT(date_inscribed) AS 'Número de sítios inscritos'
    FROM Sitios
    GROUP BY date_inscribed
    ORDER BY COUNT(date_inscribed) desc;
    """
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query and fetch results
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        return results
    except sqlite3.Error as e:
        print("An error occurred:", e)
        return []
    finally:
        conn.close()

def get_secondary_dates_count(db_path="WorldHeritage.db"):
    """
    Execute the query to extract and count secondary dates.
    """
    sql_query = """
    WITH RECURSIVE split_date AS (
        SELECT 
            sitioid,
            name_en,
            TRIM(SUBSTR(secondary_dates, 1, INSTR(secondary_dates || ',', ',') - 1)) AS secondary_date,
            SUBSTR(secondary_dates, INSTR(secondary_dates || ',', ',') + 1) AS remaining_date
        FROM sitios

        UNION ALL

        SELECT 
            sitioid,
            name_en,
            TRIM(SUBSTR(remaining_date, 1, INSTR(remaining_date || ',', ',') - 1)) AS secondary_date,
            SUBSTR(remaining_date, INSTR(remaining_date || ',', ',') + 1) AS remaining_date
        FROM split_date
        WHERE remaining_date != ''
    )
    SELECT 
        secondary_date,
        COUNT(*) AS count
    FROM split_date
    WHERE secondary_date != ''
    GROUP BY secondary_date
    ORDER BY count DESC;
    """

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()  # Fetch results as a list of tuples
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()