from si_word_freq import LetterFrequency


def main():
    lf = LetterFrequency('si', 4_000)
    lf.analyze()
    lf.draw_chart()


if __name__ == "__main__":
    main()
