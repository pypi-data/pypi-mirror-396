# NOTE: this file was AI generated.

import kdl_rs

kdl_text = """
title "Comprehensive KDL Example"

(author)person name="Alice" age=30 active=#true

coordinates 12.5 -45.8 100

numbers {
    integer 42
    negative -123
    float 3.14159
    scientific 1.23e-4
    hex 0xFF
    binary 0b1010
    octal 0o755
}

special-floats {
    positive-infinity #inf
    negative-infinity #-inf
    not-a-number #nan
}

flags {
    enabled #true
    disabled #false
    optional #null
}

text {
    simple "Hello, World!"
    escaped "Line 1\\nLine 2\\tTabbed"
    unicode "Emoji: 🎉 Math: ∑∫"
    empty ""
}

server host="localhost" port=8080 ssl=#true {
    (config)setting "max-connections" value=1000
    (config)setting "timeout" value=30
}

database type="postgresql" {
    connection host="db.example.com" port=5432 {
        credentials user="admin" password="secret"
        pool-size 10
        timeout 30
    }
    
    tables {
        - name="users" primary-key="id"
        - name="posts" primary-key="id"
        - name="comments" primary-key="id"
    }
    
    migrations {
        migration version=1 {
            up "CREATE TABLE users (id SERIAL PRIMARY KEY);"
            down "DROP TABLE users;"
        }
        migration version=2 {
            up "ALTER TABLE users ADD COLUMN email VARCHAR(255);"
            down "ALTER TABLE users DROP COLUMN email;"
        }
    }
}

mixed 42 "text" 3.14 #true #null

config-only debug=#true verbose=#false

shopping-list {
    - "Milk"
    - "Eggs"
    - "Bread"
    - "Coffee"
}

matrix {
    - 1 2 3
    - 4 5 6
    - 7 8 9
}

organization name="Tech Corp" {
    department name="Engineering" {
        team name="Backend" size=5 {
            member "Alice" role="Lead"
            member "Bob" role="Developer"
        }
        team name="Frontend" size=3 {
            member "Charlie" role="Lead"
        }
    }
    department name="Sales" {
        team name="Enterprise" size=10
    }
}

edge-cases {
    single-arg "alone"
    multiple-props a=1 b=2 c=3
    (typed)annotated-empty
    args-and-props "arg1" "arg2" key1="value1" key2="value2"
}
"""


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def explore_node(node, indent=0):
    prefix = "  " * indent

    type_str = f"({node.ty})" if node.ty else ""
    print(f"{prefix}Node: {type_str}{node.name}")

    if node.args:
        print(f"{prefix}  Args: {node.args}")

    if node.props:
        print(f"{prefix}  Props: {dict(node.props)}")

    if node.children:
        for child in node.children.nodes:
            explore_node(child, indent + 1)


def main():
    doc = kdl_rs.parse(kdl_text)

    print_section("1. Basic Node Access")
    title = doc.get("title")
    if title and title.args:
        print(f"Title: {title.args[0]}")

    print_section("2. Type Annotations")
    person = doc.get("person")
    if person:
        print(f"Node type: {person.ty}")
        print(f"Name: {person.props.get('name')}")
        print(f"Age: {person.props.get('age')}")
        print(f"Active: {person.props.get('active')}")

    print_section("3. Multiple Arguments")
    coords = doc.get("coordinates")
    if coords and coords.args:
        print(f"X: {coords.args[0]}, Y: {coords.args[1]}, Z: {coords.args[2]}")

    print_section("4. Different Number Types")
    numbers = doc.get("numbers")
    if numbers and numbers.children:
        for node in numbers.children.nodes:
            if node.args:
                print(
                    f"{node.name}: {node.args[0]} (type: {type(node.args[0]).__name__})"
                )

    print_section("5. Special Float Values")
    special = doc.get("special-floats")
    if special and special.children:
        for node in special.children.nodes:
            if node.args:
                value = node.args[0]
                print(f"{node.name}: {value}")
                if isinstance(value, float):
                    import math

                    if math.isinf(value):
                        print(f"  -> Is infinity: {value > 0}")
                    elif math.isnan(value):
                        print(f"  -> Is NaN")

    print_section("6. Boolean and Null Values")
    flags = doc.get("flags")
    if flags and flags.children:
        for node in flags.children.nodes:
            if node.args:
                print(
                    f"{node.name}: {node.args[0]} (type: {type(node.args[0]).__name__})"
                )

    print_section("7. String Types")
    text = doc.get("text")
    if text and text.children:
        for node in text.children.nodes:
            if node.args:
                print(f"{node.name}: {repr(node.args[0])}")

    print_section("8. Node with Properties")
    server = doc.get("server")
    if server:
        print(f"Host: {server.props.get('host')}")
        print(f"Port: {server.props.get('port')}")
        print(f"SSL: {server.props.get('ssl')}")

        if server.children:
            print("\nServer settings:")
            for setting in server.children.nodes:
                if setting.ty == "config":
                    name = setting.args[0] if setting.args else "unknown"
                    value = setting.props.get("value", "N/A")
                    print(f"  {name}: {value}")

    print_section("9. Complex Nested Structure")
    database = doc.get("database")
    if database and database.children:
        conn = database.children.get("connection")
        if conn:
            print(f"Database: {database.props.get('type')}")
            print(f"Host: {conn.props.get('host')}")
            print(f"Port: {conn.props.get('port')}")

            if conn.children:
                creds = conn.children.get("credentials")
                if creds:
                    print(f"User: {creds.props.get('user')}")

        tables = database.children.get("tables")
        if tables and tables.children:
            print("\nTables:")
            for table in tables.children.nodes:
                if table.name == "-":
                    name = table.props.get("name")
                    pk = table.props.get("primary-key")
                    print(f"  - {name} (PK: {pk})")

    print_section("10. Array Convention (Dash Nodes)")
    shopping = doc.get("shopping-list")
    if shopping and shopping.children:
        print("Shopping List:")
        for item in shopping.children.nodes:
            if item.name == "-" and item.args:
                print(f"  • {item.args[0]}")

    print_section("11. Multi-dimensional Data")
    matrix = doc.get("matrix")
    if matrix and matrix.children:
        print("Matrix:")
        for row in matrix.children.nodes:
            if row.name == "-" and row.args:
                print(f"  {row.args}")

    print_section("12. Deep Hierarchical Structure")
    org = doc.get("organization")
    if org and org.children:
        print(f"Organization: {org.props.get('name')}")
        for dept in org.children.nodes:
            if dept.name == "department":
                print(f"\n  Department: {dept.props.get('name')}")
                if dept.children:
                    for team in dept.children.nodes:
                        if team.name == "team":
                            team_name = team.props.get("name")
                            team_size = team.props.get("size")
                            print(f"    Team: {team_name} (Size: {team_size})")

                            if team.children:
                                for member in team.children.nodes:
                                    if member.args:
                                        name = member.args[0]
                                        role = member.props.get("role", "N/A")
                                        print(f"      - {name} ({role})")

    print_section("13. Edge Cases")
    edge = doc.get("edge-cases")
    if edge and edge.children:
        for node in edge.children.nodes:
            print(f"\n{node.name}:")
            if node.ty:
                print(f"  Type: {node.ty}")
            if node.args:
                print(f"  Args: {node.args}")
            if node.props:
                print(f"  Props: {dict(node.props)}")

    print_section("14. Complete Document Tree")
    print("First 5 top-level nodes:")
    for i, node in enumerate(doc.nodes[:5]):
        explore_node(node)
        if i < 4:
            print()

    print_section("15. Document Round-trip")
    print("Original document can be serialized back:")
    print(doc.to_string()[:200] + "...")
    print(f"\nTotal characters: {len(doc.to_string())}")

    print_section("Summary")
    print(f"Total top-level nodes: {len(doc.nodes)}")

    node_types = {}
    for node in doc.nodes:
        if node.ty:
            node_types[node.ty] = node_types.get(node.ty, 0) + 1

    if node_types:
        print(f"Typed nodes: {node_types}")

    print("\n✓ All KDL features demonstrated successfully!")


if __name__ == "__main__":
    main()
