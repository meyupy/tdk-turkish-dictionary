import json
import csv

def clean_sort_dictionary(input_json_path, output_json_path, output_csv_path):
    """
    Cleans a Turkish dictionary JSON lines file:
    - Keeps only entries and meanings
    - Removes '►' from meanings
    - Adds (I)-(IV) for 'kac' > 0
    - Sorts according to Turkish alphabet and kac
    - Saves as clean JSON and CSV (meanings separated by '|')
    """
    turkish_alphabet = "abcçdefgğhıijklmnoöprsştuüvyz"
    order_map = {c: i for i, c in enumerate(turkish_alphabet)}
    roman_map = {1: "I", 2: "II", 3: "III", 4: "IV"}

    def turkish_key(word):
        return [order_map.get(c, 999) for c in word.lower()]

    cleaned_data = []

    # Read input JSON lines
    with open(input_json_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            base_madde = entry.get("madde")
            kac = int(entry.get("kac", "0"))
            madde = base_madde
            if kac > 0 and kac in roman_map:
                madde = f"{base_madde} ({roman_map[kac]})"

            meanings = []
            for a in entry.get("anlamlarListe", []):
                anlam = a.get("anlam")
                if anlam:
                    cleaned_anlam = anlam.replace("►", "").strip()
                    meanings.append(cleaned_anlam)

            if base_madde and meanings:
                cleaned_data.append({
                    "madde": madde,
                    "anlamlar": meanings,
                    "_base_madde": base_madde.lower(),
                    "_kac": kac
                })

    # Sort by Turkish alphabet + kac
    sorted_cleaned_data = sorted(
        cleaned_data,
        key=lambda x: (turkish_key(x["_base_madde"]), x["_kac"])
    )

    # Remove helper keys
    for entry in sorted_cleaned_data:
        entry.pop("_base_madde")
        entry.pop("_kac")

    # Save to JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(sorted_cleaned_data, f, ensure_ascii=False, indent=2)

    # Save to CSV
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["madde", "anlamlar"])
        for entry in sorted_cleaned_data:
            writer.writerow([entry["madde"], " | ".join(entry["anlamlar"])])

    print(f"Cleaned and sorted dictionary saved as {output_json_path} and {output_csv_path}")

clean_sort_dictionary(
    "base_data.json",
    "turkish_dict.json",
    "turkish_dict.csv"
)