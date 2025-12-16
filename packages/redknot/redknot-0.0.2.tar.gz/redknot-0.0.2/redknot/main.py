import os
import sys

def main():

    if "-version" in sys.argv:
        print("RedKnot Version 0.0.2")
        print("By Sanyam Asthana")
        print()
        print("MIT License, 2025")
        sys.exit(0)
    
    if "-help" in sys.argv:
        print("Usage: redknot")
        print("Run the command in the folder with the project")
        print()
        print("You can redirect the output of redknot to an HTML file:")
        print("redknot > index.html")
        print()
        print("Flags:")
        print("-html : Formats the mermaid.js output in a simple HTML file.")
        print("-nocomm : Does not output comments in the mermaid.js output. HTML mode enables this by default.")
        sys.exit(0)

    files = list(os.listdir())

    includeDict = {}

    for file in files:
        includeDict.update({file:[]})

    for file in files:

        try:
            with open(file, "r") as fileObject:
                fileLines = fileObject.readlines()

                for line in fileLines:
                    if line.startswith("#include"):
                        includedFile = line.split("#include")[1].strip()[1:-1]
                        includeDict[file].append(includedFile)
        except:
            if "-html" not in sys.argv and "-nocomm" not in sys.argv:
                print(f"%% Error reading file: {file}")


    finalLines = ["graph TD"]

    if "-html" in sys.argv:
        print(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RedKnot Graph</title>
        </head>
        <body>
            <pre class="mermaid">
        """)

    for file in includeDict:
        for include in includeDict[file]:
            finalLines.append(f"{include} --> {file}")

    for i in finalLines:
        print(i)

    if "-html" in sys.argv:
        print(f"""
            </pre>

            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
            </script>
        </body>
        </html>
        """)

if __name__ == "__main__":
    main()
