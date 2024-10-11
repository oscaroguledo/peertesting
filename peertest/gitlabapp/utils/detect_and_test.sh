#!/bin/bash

# Detect files in the test directory
TEST_FILES=$(find ./test -type f)

# Function to append detected language to LANGUAGE array in .env
append_language_to_env() {
    local lang=$1
    if grep -q '^LANGUAGE=' .env; then
        sed -i "s/^LANGUAGE=\(.*\)$/LANGUAGE=\1,$lang/" .env
    else
        echo "LANGUAGE=$lang" >> .env
    fi
}

# Function to detect language based on file extension
detect_language_based_on_extension() {
    for file in $TEST_FILES; do
        case "$file" in
            *.py)    echo "Python detected based on file extension."; append_language_to_env "python"; return 0 ;;
            *.js)    echo "Node.js detected based on file extension."; append_language_to_env "nodejs"; return 0 ;;
            *.java)  echo "Java detected based on file extension."; append_language_to_env "java"; return 0 ;;
            *.c)     echo "C detected based on file extension."; append_language_to_env "c"; return 0 ;;
            *.cpp)   echo "C++ detected based on file extension."; append_language_to_env "cpp"; return 0 ;;
            *.go)    echo "Go detected based on file extension."; append_language_to_env "go"; return 0 ;;
            *.rs)    echo "Rust detected based on file extension."; append_language_to_env "rust"; return 0 ;;
            *.rb)    echo "Ruby detected based on file extension."; append_language_to_env "ruby"; return 0 ;;
            *.php)   echo "PHP detected based on file extension."; append_language_to_env "php"; return 0 ;;
            *.pl)    echo "Perl detected based on file extension."; append_language_to_env "perl"; return 0 ;;
            *.swift) echo "Swift detected based on file extension."; append_language_to_env "swift"; return 0 ;;
            *.r)     echo "R detected based on file extension."; append_language_to_env "r"; return 0 ;;
            *.ts)    echo "TypeScript detected based on file extension."; append_language_to_env "typescript"; return 0 ;;
            *.m)     echo "Objective-C detected based on file extension."; append_language_to_env "objective-c"; return 0 ;;
            *.sql)   echo "SQL detected based on file extension."; append_language_to_env "sql"; return 0 ;;
            *.groovy) echo "Groovy detected based on file extension."; append_language_to_env "groovy"; return 0 ;;
            *.scala) echo "Scala detected based on file extension."; append_language_to_env "scala"; return 0 ;;
            *.dart)  echo "Dart detected based on file extension."; append_language_to_env "dart"; return 0 ;;
            *.lua)   echo "Lua detected based on file extension."; append_language_to_env "lua"; return 0 ;;
            *.jl)    echo "Julia detected based on file extension."; append_language_to_env "julia"; return 0 ;;
            *.hs)    echo "Haskell detected based on file extension."; append_language_to_env "haskell"; return 0 ;;
            *.sh)    echo "Shell Script detected based on file extension."; append_language_to_env "shell"; return 0 ;;
            *.ps1)   echo "PowerShell detected based on file extension."; append_language_to_env "powershell"; return 0 ;;
            *.vb)    echo "Visual Basic detected based on file extension."; append_language_to_env "vb"; return 0 ;;
            *.asm)   echo "Assembly detected based on file extension."; append_language_to_env "assembly"; return 0 ;;
            *.vhd|*.vhdl) echo "VHDL detected based on file extension."; append_language_to_env "vhdl"; return 0 ;;
            *.v)     echo "Verilog detected based on file extension."; append_language_to_env "verilog"; return 0 ;;
            *.pas)   echo "Pascal detected based on file extension."; append_language_to_env "pascal"; return 0 ;;
            *.tcl)   echo "Tcl detected based on file extension."; append_language_to_env "tcl"; return 0 ;;
            *.rkt)   echo "Racket detected based on file extension."; append_language_to_env "racket"; return 0 ;;
            *.coffee) echo "CoffeeScript detected based on file extension."; append_language_to_env "coffeescript"; return 0 ;;
            *.hx)    echo "Haxe detected based on file extension."; append_language_to_env "haxe"; return 0 ;;
            *.awk)   echo "AWK detected based on file extension."; append_language_to_env "awk"; return 0 ;;
            *.nim)   echo "Nim detected based on file extension."; append_language_to_env "nim"; return 0 ;;
            *.cr)    echo "Crystal detected based on file extension."; append_language_to_env "crystal"; return 0 ;;
            *.lisp|*.lsp) echo "Lisp detected based on file extension."; append_language_to_env "lisp"; return 0 ;;
            *.clj|*.cljs|*.cljc) echo "Clojure detected based on file extension."; append_language_to_env "clojure"; return 0 ;;
            *.fth|*.4th) echo "Forth detected based on file extension."; append_language_to_env "forth"; return 0 ;;
            *.pike)  echo "Pike detected based on file extension."; append_language_to_env "pike"; return 0 ;;
            *.zig)   echo "Zig detected based on file extension."; append_language_to_env "zig"; return 0 ;;
            *.elm)   echo "Elm detected based on file extension."; append_language_to_env "elm"; return 0 ;;
            *.sml|*.sig) echo "SML detected based on file extension."; append_language_to_env "sml"; return 0 ;;
            *.agda)  echo "Agda detected based on file extension."; append_language_to_env "agda"; return 0 ;;
            *.v)     echo "Coq detected based on file extension."; append_language_to_env "coq"; return 0 ;;
            *.d)     echo "D detected based on file extension."; append_language_to_env "d"; return 0 ;;
            *.lgt)   echo "Logtalk detected based on file extension."; append_language_to_env "logtalk"; return 0 ;;
            *.m|*.mo) echo "Mercury detected based on file extension."; append_language_to_env "mercury"; return 0 ;;
            *.k)     echo "K detected based on file extension."; append_language_to_env "k"; return 0 ;;
            *.t)     echo "Turing detected based on file extension."; append_language_to_env "turing"; return 0 ;;
            *.purs)  echo "PureScript detected based on file extension."; append_language_to_env "purescript"; return 0 ;;
            *.pony)  echo "Pony detected based on file extension."; append_language_to_env "pony"; return 0 ;;
            *.icn)   echo "Icon detected based on file extension."; append_language_to_env "icon"; return 0 ;;
            *.mod)   echo "Modula-2 detected based on file extension."; append_language_to_env "modula-2"; return 0 ;;
            *.bmx)   echo "BlitzMax detected based on file extension."; append_language_to_env "blitzmax"; return 0 ;;
            *.dylan) echo "Dylan detected based on file extension."; append_language_to_env "dylan"; return 0 ;;
            *.nix)   echo "Nix detected based on file extension."; append_language_to_env "nix"; return 0 ;;
            *.gms)   echo "GAMS detected based on file extension."; append_language_to_env "gams"; return 0 ;;
            *.idr)   echo "Idris detected based on file extension."; append_language_to_env "idris"; return 0 ;;
            *.ijs)   echo "J detected based on file extension."; append_language_to_env "j"; return 0 ;;
            *.io)    echo "Io detected based on file extension."; append_language_to_env "io"; return 0 ;;
            *.r)     echo "Rebol detected based on file extension."; append_language_to_env "rebol"; return 0 ;;
            *.cfm|*.cfc) echo "ColdFusion detected based on file extension."; append_language_to_env "coldfusion"; return 0 ;;
            *.rpg)   echo "RPG detected based on file extension."; append_language_to_env "rpg"; return 0 ;;
            *.clp)   echo "CLIPS detected based on file extension."; append_language_to_env "clips"; return 0 ;;
            *.vala|*.vapi) echo "Vala detected based on file extension."; append_language_to_env "vala"; return 0 ;;
            *.rpg)   echo "RPGLE detected based on file extension."; append_language_to_env "rpg"; return 0 ;;
            *.sd7)   echo "Seed7 detected based on file extension."; append_language_to_env "seed7"; return 0 ;;
            *.q)     echo "Q detected based on file extension."; append_language_to_env "q"; return 0 ;;
            *.mq4)   echo "MQL4 detected based on file extension."; append_language_to_env "mql4"; return 0 ;;
            *.mq5)   echo "MQL5 detected based on file extension."; append_language_to_env "mql5"; return 0 ;;
            *.mls)   echo "OCamlScript detected based on file extension."; append_language_to_env "ocamlscript"; return 0 ;;
            *.sas)   echo "SAS detected based on file extension."; append_language_to_env "sas"; return 0 ;;
            *.ads|*.adb) echo "SPARK detected based on file extension."; append_language_to_env "spark"; return 0 ;;
            *.yaml|*.yml) echo "YAML detected based on file extension."; append_language_to_env "yaml"; return 0 ;;
            *.feature) echo "Gherkin detected based on file extension."; append_language_to_env "gherkin"; return 0 ;;
            *.txt)   echo "No language detected."; append_language_to_env "none"; return 0 ;;
            *)       echo "No language detected."; append_language_to_env "none"; return 0 ;;
        esac
    done
}

# Function to detect language based on file content (if needed)
detect_language_based_on_content() {
    for file in $TEST_FILES; do
        if grep -q 'import unittest' "$file"; then
            echo "Python detected based on file content."
            append_language_to_env "python"
            return 0
        elif grep -q 'const' "$file" && grep -q 'require(' "$file"; then
            echo "Node.js detected based on file content."
            append_language_to_env "nodejs"
            return 0
        elif grep -q 'import org.junit' "$file"; then
            echo "Java detected based on file content."
            append_language_to_env "java"
            return 0
        elif grep -q '#include' "$file" && grep -q '<stdio.h>' "$file"; then
            echo "C detected based on file content."
            append_language_to_env "c"
            return 0
        elif grep -q '#include' "$file" && grep -q '<iostream>' "$file"; then
            echo "C++ detected based on file content."
            append_language_to_env "cpp"
            return 0
        elif grep -q 'package' "$file" && grep -q 'import' "$file"; then
            echo "Go detected based on file content."
            append_language_to_env "go"
            return 0
        elif grep -q 'extern crate' "$file" || grep -q 'use ' "$file"; then
            echo "Rust detected based on file content."
            append_language_to_env "rust"
            return 0
        elif grep -q 'require ' "$file" || grep -q 'RSpec.describe' "$file"; then
            echo "Ruby detected based on file content."
            append_language_to_env "ruby"
            return 0
        elif grep -q 'class ' "$file" && grep -q 'public function' "$file"; then
            echo "PHP detected based on file content."
            append_language_to_env "php"
            return 0
        elif grep -q 'use ' "$file" || grep -q 'print ' "$file"; then
            echo "Perl detected based on file content."
            append_language_to_env "perl"
            return 0
        elif grep -q 'import ' "$file" || grep -q 'func ' "$file"; then
            echo "Swift detected based on file content."
            append_language_to_env "swift"
            return 0
        elif grep -q 'console.log' "$file" || grep -q 'function ' "$file"; then
            echo "JavaScript detected based on file content."
            append_language_to_env "javascript"
            return 0
        elif grep -q 'def ' "$file" || grep -q 'class ' "$file"; then
            echo "Ruby detected based on file content."
            append_language_to_env "ruby"
            return 0
        elif grep -q 'BEGIN {' "$file" || grep -q '}' "$file"; then
            echo "AWK detected based on file content."
            append_language_to_env "awk"
            return 0
        elif grep -q 'package ' "$file" || grep -q 'import ' "$file"; then
            echo "Kotlin detected based on file content."
            append_language_to_env "kotlin"
            return 0
        else
            echo "No language detected."
            append_language_to_env "none"
            return 0
        fi
    done
}

# Attempt to detect language based on file extensions first
detect_language_based_on_extension

# If no language detected based on extensions, attempt to detect based on content
if [ $? -ne 0 ]; then
    detect_language_based_on_content
fi

# If still no language detected, output a message and exit with error
if [ $? -ne 0 ]; then
    echo "No recognized test files found. Unable to detect language."
    exit 1
fi
