import os
import re
import json
import time
import shutil
import requests

from pathlib import Path


# ================================================================
# CONFIGURATION
# ================================================================

REPO_ROOT = Path(".")

README_FILE = REPO_ROOT / "README.md"
STATS_FILE = REPO_ROOT / "stats.json"

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"


# ================================================================
# REQUEST HEADERS
# ================================================================

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}


# ================================================================
# SOURCE FILE EXTENSIONS
# ================================================================

SOURCE_EXTENSIONS = {
    ".java",
    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".py",
    ".js",
    ".ts",
    ".go",
    ".rs",
    ".kt"
}


# ================================================================
# IGNORE DIRECTORIES
# ================================================================

IGNORE_DIRS = {
    ".git",
    ".github",
    ".vscode",
    ".idea",
    "__pycache__",
    "node_modules"
}


# ================================================================
# IGNORE FILES
# ================================================================

IGNORE_FILES = {
    "README.md",
    "stats.json",
    "generate_readme.py"
}


# ================================================================
# DOMAIN FOLDER MAPPING
# ================================================================

DOMAIN_FOLDER_NAMES = {

    "Array": "Array",

    "String": "String",

    "Hash Table": "Hash-Table",

    "Two Pointers": "Two-Pointers",

    "Binary Search": "Binary-Search",

    "Bit Manipulation": "Bit-Manipulation",

    "Math": "Math",

    "Prefix Sum": "Prefix-Sum",

    "Sliding Window": "Sliding-Window",

    "Sorting": "Sorting",

    "Stack": "Stack",

    "Queue": "Queue",

    "Linked List": "Linked-List",

    "Tree": "Tree",

    "Trie": "Trie",

    "Heap": "Heap",

    "Graph": "Graph",

    "Greedy": "Greedy",

    "Dynamic Programming": "Dynamic-Programming",

    "Backtracking": "Backtracking",

    "Divide and Conquer": "Divide-and-Conquer",

    "Recursion": "Recursion",

    "Simulation": "Simulation",

    "String Matching": "String-Matching",

    "Number Theory": "Number-Theory",

    "Boyer-Moore String-Search Algorithm":
        "Boyer-Moore-String-Search-Algorithm",

    "Knuth-Morris-Pratt Algorithm":
        "Knuth-Morris-Pratt-Algorithm",

    "Z Algorithm":
        "Z-Algorithm"
}


# ================================================================
# DEFAULT DOMAIN PRIORITY
# ================================================================

TOPIC_PRIORITY = [

    "Array",
    "String",
    "Hash Table",
    "Two Pointers",
    "Binary Search",
    "Bit Manipulation",
    "Math",
    "Prefix Sum",
    "Sliding Window",
    "Sorting",
    "Stack",
    "Queue",
    "Linked List",
    "Tree",
    "Trie",
    "Heap",
    "Graph",
    "Greedy",
    "Dynamic Programming",
    "Backtracking",
    "Divide and Conquer",
    "Recursion",
    "Simulation",
    "String Matching",
    "Number Theory",
    "Boyer-Moore String-Search Algorithm",
    "Knuth-Morris-Pratt Algorithm",
    "Z Algorithm"
]


# ================================================================
# PRIMARY DOMAIN OVERRIDES
#
# IMPORTANT:
# Some LeetCode problems have multiple tags.
# These overrides define the domain you want to use
# for the physical folder and README primary-domain column.
#
# Add more problems here whenever you want a specific
# primary domain.
# ================================================================

DOMAIN_OVERRIDES = {

    # String problems
    "longest-common-prefix": "String",
    "roman-to-integer": "String",
    "find-the-index-of-the-first-occurrence-in-a-string": "String",
    "valid-palindrome": "String",
    "defanging-an-ip-address": "String",

    # Binary Search problems
    "binary-search": "Binary Search",
    "find-minimum-in-rotated-sorted-array": "Binary Search",

    # Bit Manipulation problems
    "power-of-two": "Bit Manipulation",
    "power-of-four": "Bit Manipulation",

    # Math problems
    "add-digits": "Math",
    "power-of-three": "Math",

    # Array problems
    "two-sum": "Array",
    "median-of-two-sorted-arrays": "Array",
    "remove-duplicates-from-sorted-array": "Array",
    "remove-element": "Array",
    "first-missing-positive": "Array",
    "plus-one": "Array",
    "missing-number": "Array",
    "find-the-duplicate-number": "Array",
    "third-maximum-number": "Array",
    "running-sum-of-1d-array": "Array",
    "number-of-good-pairs": "Array"
}


# ================================================================
# LANGUAGE MAP
# ================================================================

LANGUAGE_MAP = {

    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".kt": "Kotlin"
}


# ================================================================
# NORMALIZE SLUG
# ================================================================

def normalize_slug(value):

    value = value.strip().lower()

    # Remove leading problem number
    value = re.sub(
        r"^\d+[\s._-]+",
        "",
        value
    )

    value = value.replace("_", "-")

    value = re.sub(
        r"\s+",
        "-",
        value
    )

    value = re.sub(
        r"[^a-z0-9-]",
        "",
        value
    )

    value = re.sub(
        r"-+",
        "-",
        value
    )

    return value.strip("-")


# ================================================================
# CHECK SOURCE FILE
# ================================================================

def contains_source_code(folder):

    try:

        for file in folder.iterdir():

            if not file.is_file():
                continue

            if file.name in IGNORE_FILES:
                continue

            if file.suffix.lower() in SOURCE_EXTENSIONS:
                return True

    except Exception:
        return False

    return False


# ================================================================
# FIND ALL PROBLEM FOLDERS
#
# Detects BOTH:
#
# two-sum/
#
# AND:
#
# Array/two-sum/
#
# ================================================================

def find_problem_folders():

    found = []

    for root, dirs, files in os.walk(REPO_ROOT):

        root_path = Path(root)

        # Ignore directories
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
            and not d.startswith(".")
        ]

        # Ignore hidden paths
        if any(
            part.startswith(".")
            for part in root_path.parts
        ):
            continue

        # Never treat repository root as a problem
        if root_path == REPO_ROOT:
            continue

        # Check for source files
        source_found = False

        for filename in files:

            if filename in IGNORE_FILES:
                continue

            extension = Path(
                filename
            ).suffix.lower()

            if extension in SOURCE_EXTENSIONS:

                source_found = True
                break

        if source_found:

            found.append(root_path)

            # Do not search inside a problem folder
            dirs[:] = []

    return found


# ================================================================
# GET LANGUAGE
# ================================================================

def get_language(folder):

    languages = []

    try:

        for file in folder.iterdir():

            if not file.is_file():
                continue

            extension = file.suffix.lower()

            if extension in LANGUAGE_MAP:

                language = LANGUAGE_MAP[
                    extension
                ]

                if language not in languages:

                    languages.append(
                        language
                    )

    except Exception:
        pass

    if not languages:
        return "Unknown"

    return ", ".join(languages)


# ================================================================
# GET SLUG
# ================================================================

def get_slug(folder):

    return normalize_slug(
        folder.name
    )


# ================================================================
# LEETCODE GRAPHQL
# ================================================================

def get_problem(slug):

    query = """
    query questionData($titleSlug: String!) {

        question(titleSlug: $titleSlug) {

            questionFrontendId

            title

            titleSlug

            difficulty

            topicTags {
                name
            }
        }
    }
    """

    payload = {

        "query": query,

        "variables": {
            "titleSlug": slug
        }
    }


    for attempt in range(3):

        try:

            response = requests.post(

                LEETCODE_GRAPHQL,

                json=payload,

                headers=HEADERS,

                timeout=30
            )


            if response.status_code != 200:

                print(
                    f"API status "
                    f"{response.status_code} "
                    f"for {slug}"
                )

                time.sleep(2)

                continue


            data = response.json()


            if "data" not in data:

                time.sleep(2)

                continue


            question = (
                data["data"]
                .get("question")
            )


            if question:

                return question


            print(
                f"No LeetCode metadata "
                f"found for: {slug}"
            )

            return None


        except Exception as error:

            print(
                f"API error for {slug}: "
                f"{error}"
            )

            time.sleep(2)


    return None


# ================================================================
# FALLBACK TITLE
# ================================================================

def title_from_slug(slug):

    words = slug.replace(
        "-",
        " "
    ).split()

    return " ".join(
        word.capitalize()
        for word in words
    )


# ================================================================
# GET CURRENT DOMAIN
# ================================================================

def get_current_domain(folder):

    if folder.parent == REPO_ROOT:

        return None


    parent_name = folder.parent.name


    for topic, folder_name in (
        DOMAIN_FOLDER_NAMES.items()
    ):

        if (
            parent_name.lower()
            == folder_name.lower()
        ):

            return topic


    return None


# ================================================================
# GET PRIMARY DOMAIN
#
# OVERRIDE HAS HIGHEST PRIORITY.
# ================================================================

def get_primary_domain(
    slug,
    tags,
    current_domain=None
):

    # ------------------------------------------------------------
    # 1. MANUAL OVERRIDE
    # ------------------------------------------------------------

    if slug in DOMAIN_OVERRIDES:

        return DOMAIN_OVERRIDES[
            slug
        ]


    # ------------------------------------------------------------
    # 2. KEEP CURRENT DOMAIN IF IT MATCHES
    # ------------------------------------------------------------

    if current_domain:

        if current_domain in tags:

            return current_domain


    # ------------------------------------------------------------
    # 3. USE DEFAULT TOPIC PRIORITY
    # ------------------------------------------------------------

    for topic in TOPIC_PRIORITY:

        if topic in tags:

            return topic


    # ------------------------------------------------------------
    # 4. UNCATEGORIZED
    # ------------------------------------------------------------

    return "Uncategorized"


# ================================================================
# MOVE PROBLEM
# ================================================================

def organize_problem(
    folder,
    primary_domain
):

    if primary_domain == "Uncategorized":

        return folder


    domain_folder_name = (
        DOMAIN_FOLDER_NAMES.get(
            primary_domain,
            primary_domain
        )
    )


    target_domain = (
        REPO_ROOT
        / domain_folder_name
    )


    target_domain.mkdir(
        parents=True,
        exist_ok=True
    )


    target_folder = (
        target_domain
        / folder.name
    )


    # Already correct
    try:

        if (
            folder.resolve()
            == target_folder.resolve()
        ):

            return target_folder

    except Exception:
        pass


    # ------------------------------------------------------------
    # TARGET ALREADY EXISTS
    # ------------------------------------------------------------

    if target_folder.exists():

        print(
            f"Target already exists: "
            f"{target_folder}"
        )

        return target_folder


    # ------------------------------------------------------------
    # MOVE
    # ------------------------------------------------------------

    print("")
    print("MOVING PROBLEM")
    print("------------------------------")
    print(f"FROM : {folder}")
    print(f"TO   : {target_folder}")
    print("------------------------------")


    try:

        shutil.move(
            str(folder),
            str(target_folder)
        )

        return target_folder


    except Exception as error:

        print(
            f"Could not move "
            f"{folder}: {error}"
        )

        return folder


# ================================================================
# COLLECT PROBLEMS
# ================================================================

def collect_problems():

    print("")
    print(
        "=============================================="
    )
    print(
        "SCANNING ALL LEETCODE SOLUTIONS"
    )
    print(
        "=============================================="
    )
    print("")


    folders = find_problem_folders()


    print(
        f"Found {len(folders)} solution folders"
    )

    print("")


    problems = {}


    for folder in folders:

        slug = get_slug(folder)


        if not slug:

            continue


        # Avoid duplicate problem
        if slug in problems:

            print(
                f"Duplicate ignored: {slug}"
            )

            continue


        print(
            f"Processing: {slug}"
        )


        # --------------------------------------------------------
        # GET LEETCODE DATA
        # --------------------------------------------------------

        metadata = get_problem(
            slug
        )


        # --------------------------------------------------------
        # API SUCCESS
        # --------------------------------------------------------

        if metadata:

            number = int(
                metadata[
                    "questionFrontendId"
                ]
            )


            title = metadata[
                "title"
            ]


            difficulty = metadata[
                "difficulty"
            ]


            tags = [

                tag["name"]

                for tag in metadata.get(
                    "topicTags",
                    []
                )

            ]


        # --------------------------------------------------------
        # API FAILURE
        # DO NOT REMOVE THE PROBLEM
        # --------------------------------------------------------

        else:

            print(
                f"Using fallback data "
                f"for {slug}"
            )


            number = 999999

            title = title_from_slug(
                slug
            )

            difficulty = "Unknown"

            tags = []


        # --------------------------------------------------------
        # CURRENT DOMAIN
        # --------------------------------------------------------

        current_domain = (
            get_current_domain(
                folder
            )
        )


        # --------------------------------------------------------
        # PRIMARY DOMAIN
        # --------------------------------------------------------

        primary_domain = (
            get_primary_domain(

                slug,

                tags,

                current_domain

            )
        )


        # --------------------------------------------------------
        # LANGUAGE
        # --------------------------------------------------------

        language = get_language(
            folder
        )


        # --------------------------------------------------------
        # STORE
        # --------------------------------------------------------

        problems[slug] = {

            "number": number,

            "title": title,

            "slug": slug,

            "difficulty": difficulty,

            "language": language,

            "tags": tags,

            "primary_domain":
                primary_domain,

            "folder":
                str(folder)

        }


    return problems


# ================================================================
# ORGANIZE PROBLEMS
# ================================================================

def organize_all_problems(
    problems
):

    print("")
    print(
        "=============================================="
    )
    print(
        "ORGANIZING PROBLEM FOLDERS"
    )
    print(
        "=============================================="
    )
    print("")


    for slug, problem in list(
        problems.items()
    ):

        folder = Path(
            problem["folder"]
        )


        if not folder.exists():

            continue


        primary_domain = (
            problem[
                "primary_domain"
            ]
        )


        new_folder = (
            organize_problem(

                folder,

                primary_domain

            )
        )


        problem[
            "folder"
        ] = str(
            new_folder
        )


# ================================================================
# SORT PROBLEMS
# ================================================================

def sort_problems(problems):

    def sort_key(problem):

        number = problem[
            "number"
        ]


        if number == 999999:

            return (
                999999,
                problem[
                    "title"
                ].lower()
            )


        return (
            number,
            problem[
                "title"
            ].lower()
        )


    return sorted(
        problems.values(),
        key=sort_key
    )


# ================================================================
# CREATE CATEGORY LIST
#
# A problem can appear in multiple LeetCode categories.
# ================================================================

def create_categories(
    all_problems
):

    categories = {}


    for problem in all_problems:

        for tag in problem[
            "tags"
        ]:

            if tag not in categories:

                categories[tag] = []


            categories[
                tag
            ].append(
                problem
            )


    # Sort
    for category in categories:

        categories[
            category
        ].sort(

            key=lambda x: (

                x["number"],

                x["title"].lower()

            )

        )


    return categories


# ================================================================
# ORDER CATEGORIES
# ================================================================

def order_categories(
    categories
):

    ordered = []


    for topic in TOPIC_PRIORITY:

        if topic in categories:

            ordered.append(
                topic
            )


    for topic in sorted(
        categories
    ):

        if topic not in ordered:

            ordered.append(
                topic
            )


    return ordered


# ================================================================
# GENERATE README
# ================================================================

def generate_readme(
    all_problems
):

    # ------------------------------------------------------------
    # DIFFICULTY COUNTS
    # ------------------------------------------------------------

    easy = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Easy"

    )


    medium = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Medium"

    )


    hard = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Hard"

    )


    unknown = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Unknown"

    )


    total = len(
        all_problems
    )


    # ------------------------------------------------------------
    # CATEGORIES
    # ------------------------------------------------------------

    categories = create_categories(
        all_problems
    )


    ordered_categories = (
        order_categories(
            categories
        )
    )


    # ------------------------------------------------------------
    # README ARRAY
    # ------------------------------------------------------------

    readme = []


    # ============================================================
    # HEADER
    # ============================================================

    readme.append(
        "# LeetCode_Solution"
    )

    readme.append("")

    readme.append(
        "Automatically organized "
        "LeetCode solutions and progress."
    )

    readme.append("")


    # ============================================================
    # OVERALL PROGRESS
    # ============================================================

    readme.append(
        "## 📊 Overall Progress"
    )

    readme.append("")

    readme.append(
        "| Difficulty | Solved |"
    )

    readme.append(
        "|---|---:|"
    )

    readme.append(
        f"| 🟢 Easy | {easy} |"
    )

    readme.append(
        f"| 🟡 Medium | {medium} |"
    )

    readme.append(
        f"| 🔴 Hard | {hard} |"
    )

    readme.append(
        f"| ⚪ Unknown | {unknown} |"
    )

    readme.append(
        f"| **Total Solved** | **{total}** |"
    )

    readme.append("")


    # ============================================================
    # DOMAIN SUMMARY
    # ============================================================

    readme.append(
        "## 📚 Domain Summary"
    )

    readme.append("")

    readme.append(
        "| Domain | Problems |"
    )

    readme.append(
        "|---|---:|"
    )


    domain_counts = {}


    for problem in all_problems:

        domain = problem[
            "primary_domain"
        ]


        domain_counts[
            domain
        ] = (
            domain_counts.get(
                domain,
                0
            )
            + 1
        )


    for domain in sorted(
        domain_counts,
        key=lambda x: (
            x == "Uncategorized",
            x.lower()
        )
    ):

        readme.append(

            f"| {domain} | "
            f"{domain_counts[domain]} |"

        )


    readme.append("")


    # ============================================================
    # COMPLETE PROBLEM LIST
    #
    # EACH PROBLEM APPEARS ONLY ONCE
    # ============================================================

    readme.append(
        "## 📋 Complete Problem List"
    )

    readme.append("")

    readme.append(

        "| # | Problem | LeetCode | "
        "Language | Difficulty | Domain |"

    )

    readme.append(

        "|---:|---|---|---|---|---|"

    )


    for problem in all_problems:

        number = problem[
            "number"
        ]

        title = problem[
            "title"
        ]

        slug = problem[
            "slug"
        ]

        language = problem[
            "language"
        ]

        difficulty = problem[
            "difficulty"
        ]

        domain = problem[
            "primary_domain"
        ]


        folder = Path(
            problem[
                "folder"
            ]
        )


        relative_folder = (
            folder.as_posix()
        )


        solution_link = (
            f"./{relative_folder}"
        )


        leetcode_link = (

            "https://leetcode.com/"
            "problems/"
            f"{slug}/"

        )


        number_display = (
            "-"
            if number == 999999
            else str(number)
        )


        leetcode_display = (

            "LeetCode"
            if number == 999999
            else f"LeetCode #{number}"

        )


        readme.append(

            f"| {number_display} | "
            f"[{title}]({solution_link}) | "
            f"[{leetcode_display}]"
            f"({leetcode_link}) | "
            f"{language} | "
            f"{difficulty} | "
            f"{domain} |"

        )


    readme.append("")


    # ============================================================
    # PROBLEMS BY DOMAIN
    # ============================================================

    readme.append(
        "## 🗂️ Problems by Domain"
    )

    readme.append("")


    for category in (
        ordered_categories
    ):

        category_problems = (
            categories[
                category
            ]
        )


        readme.append(
            f"### {category}"
        )

        readme.append("")


        readme.append(

            "| # | Problem | "
            "Language | Difficulty |"

        )

        readme.append(
            "|---:|---|---|---|"
        )


        for problem in (
            category_problems
        ):

            number = problem[
                "number"
            ]

            title = problem[
                "title"
            ]

            language = problem[
                "language"
            ]

            difficulty = problem[
                "difficulty"
            ]

            folder = Path(
                problem[
                    "folder"
                ]
            )


            relative_folder = (
                folder.as_posix()
            )


            number_display = (
                "-"
                if number == 999999
                else str(number)
            )


            readme.append(

                f"| {number_display} | "
                f"[{title}]"
                f"(./{relative_folder}) | "
                f"{language} | "
                f"{difficulty} |"

            )


        readme.append("")


    # ============================================================
    # FOOTER
    # ============================================================

    readme.append("---")

    readme.append("")

    readme.append(
        "🤖 Automatically updated "
        "using GitHub Actions."
    )

    readme.append("")

    readme.append(
        "📌 Primary domains are selected "
        "using configured domain rules."
    )


    # ============================================================
    # WRITE README
    # ============================================================

    README_FILE.write_text(

        "\n".join(readme),

        encoding="utf-8"

    )


# ================================================================
# GENERATE STATS.JSON
# ================================================================

def generate_stats(
    all_problems
):

    easy = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Easy"

    )


    medium = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Medium"

    )


    hard = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Hard"

    )


    unknown = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Unknown"

    )


    total = len(
        all_problems
    )


    stats = {

        "totalSolved": total,

        "easy": easy,

        "medium": medium,

        "hard": hard,

        "unknown": unknown,

        "problems": [

            {

                "number":
                    p["number"],

                "title":
                    p["title"],

                "slug":
                    p["slug"],

                "difficulty":
                    p["difficulty"],

                "language":
                    p["language"],

                "tags":
                    p["tags"],

                "primaryDomain":
                    p["primary_domain"],

                "folder":
                    p["folder"]

            }

            for p in all_problems

        ]

    }


    STATS_FILE.write_text(

        json.dumps(

            stats,

            indent=2,

            ensure_ascii=False

        ),

        encoding="utf-8"

    )


# ================================================================
# PRINT SUMMARY
# ================================================================

def print_summary(
    all_problems
):

    easy = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Easy"

    )


    medium = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Medium"

    )


    hard = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Hard"

    )


    unknown = sum(

        1

        for p in all_problems

        if p["difficulty"] == "Unknown"

    )


    total = len(
        all_problems
    )


    print("")
    print(
        "=============================================="
    )
    print(
        "LEETCODE ORGANIZATION COMPLETED"
    )
    print(
        "=============================================="
    )

    print(
        f"Easy          : {easy}"
    )

    print(
        f"Medium        : {medium}"
    )

    print(
        f"Hard          : {hard}"
    )

    print(
        f"Unknown       : {unknown}"
    )

    print(
        f"TOTAL SOLVED  : {total}"
    )

    print(
        "=============================================="
    )


    # ------------------------------------------------------------
    # DOMAIN COUNTS
    # ------------------------------------------------------------

    domain_counts = {}


    for problem in all_problems:

        domain = problem[
            "primary_domain"
        ]


        domain_counts[
            domain
        ] = (
            domain_counts.get(
                domain,
                0
            )
            + 1
        )


    print("")
    print("DOMAIN COUNTS")
    print(
        "----------------------------------------------"
    )


    for domain in sorted(
        domain_counts
    ):

        print(
            f"{domain:<40}"
            f"{domain_counts[domain]}"
        )


    print(
        "=============================================="
    )
    print("")


# ================================================================
# MAIN
# ================================================================

def main():

    print("")
    print(
        "=============================================="
    )
    print(
        "LEETCODE AUTOMATIC ORGANIZER"
    )
    print(
        "=============================================="
    )
    print("")


    # STEP 1
    problems = collect_problems()


    # STEP 2
    organize_all_problems(
        problems
    )


    # STEP 3
    all_problems = sort_problems(
        problems
    )


    # STEP 4
    generate_readme(
        all_problems
    )


    # STEP 5
    generate_stats(
        all_problems
    )


    # STEP 6
    print_summary(
        all_problems
    )


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":

    main()
  
