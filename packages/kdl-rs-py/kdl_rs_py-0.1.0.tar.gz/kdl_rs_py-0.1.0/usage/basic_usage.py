import kdl_rs


kdl_text = """
package version="1.0.0" {
    author "John Doe"
    email "abc@xyz.com"
}

config {
    debug #true
    port 8080
    host "localhost"
}
"""


def main():
    doc = kdl_rs.parse(kdl_text)

    package = doc.get("package")
    if package:
        print(f"Package version: {package.props.get('version')}\n")

    if package and package.children:
        author_node = package.children.get("author")
        email_node = package.children.get("email")
        if author_node and author_node.args:
            print(f"Author: {author_node.args[0]}")
        if email_node and email_node.args:
            print(f"Email: {email_node.args[0]}")
        print()

    config = doc.get("config")
    if config:
        print("Configuration:")

        if config.children:
            debug_node = config.children.get("debug")
            port_node = config.children.get("port")
            host_node = config.children.get("host")

            if debug_node and debug_node.args:
                print(f"  Debug: {debug_node.args[0]}")
            if port_node and port_node.args:
                print(f"  Port: {port_node.args[0]}")
            if host_node and host_node.args:
                print(f"  Host: {host_node.args[0]}")
        print()

    print("KDL Source:")
    print("-----------", end="")
    print(doc.to_string())


if __name__ == "__main__":
    main()
