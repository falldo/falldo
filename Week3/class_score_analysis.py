def read_data(filename):
    # TODO) Read `filename` as a list of integers
    data = []
    with open(filename, 'r') as file:
        for line in file.readlines():
            try:
                data.append([int(value) for value in line.split(',')])
            except ValueError:
                pass
    return data

def calc_weighted_average(data_2d, weight):
    # TODO) Calculate the weighted averages of each row of `data_2d`
    average = []
    for row in data_2d:
        average.append(sum(score * ratio for score, ratio in zip(row, weight)))
    return average

def analyze_data(data_1d):
    # TODO) Calculate summary statistics of the given `data_1d`
    # Note) Please don't use NumPy and other libraries. Do it yourself.
    mean = sum(data_1d) / len(data_1d)
    var = sum((value - mean) ** 2 for value in data_1d) / len(data_1d)

    sorted_data = sorted(data_1d)
    middle = len(sorted_data) // 2
    if len(sorted_data) % 2 == 0:
        median = (sorted_data[middle - 1] + sorted_data[middle]) / 2
    else:
        median = sorted_data[middle]
    return mean, var, median, min(data_1d), max(data_1d)

if __name__ == '__main__':
    data = read_data('data/class_score_en.csv')
    if data and len(data[0]) == 2: # Check 'data' is valid
        average = calc_weighted_average(data, [40/125, 60/100])

        # Write the analysis report as a markdown file
        with open('class_score_analysis.md', 'w') as report:
            report.write('### Individual Score\n\n')
            report.write('| Midterm | Final | Average |\n')
            report.write('| ------- | ----- | ----- |\n')
            for ((m_score, f_score), a_score) in zip(data, average):
                report.write(f'| {m_score} | {f_score} | {a_score:.3f} |\n')
            report.write('\n\n\n')

            report.write('### Examination Analysis\n')
            data_columns = {
                'Midterm': [m_score for m_score, _ in data],
                'Final'  : [f_score for _, f_score in data],
                'Average': average }
            for name, column in data_columns.items():
                mean, var, median, min_, max_ = analyze_data(column)
                report.write(f'* {name}\n')
                report.write(f'  * Mean: **{mean:.3f}**\n')
                report.write(f'  * Variance: {var:.3f}\n')
                report.write(f'  * Median: **{median:.3f}**\n')
                report.write(f'  * Min/Max: ({min_:.3f}, {max_:.3f})\n')
