import re
import math


class ParserGetDPTimeTable:
    """
    This class parses GetDP's TimeTable format output files.
    """

    def __init__(self, filePath):
        self.time_values = []
        self.values = []
        # Parse data:
        with open(filePath) as file:
            # If the first line starts with #, we skip it.
            first_line = file.readline()
            if not first_line.startswith("#"):
                number_of_entries = len(
                    re.findall(r"(-?\d+\.?\d*e?[-+]*\d*)", first_line)
                )
                # readline() moves the cursor to the next line, so we need to go back to
                # the beginning of the file.
                file.seek(0)
            else:
                second_line = file.readline()
                number_of_entries = len(
                    re.findall(r"(-?\d+\.?\d*e?[-+]*\d*)", second_line)
                )
                # Seek to the second line
                file.seek(len(first_line) + 1)

            data = file.read()

        entries = re.findall(r"(-?\d+\.?\d*e?[-+]*\d*)", data)
        if number_of_entries == 2:
            # Global scalar value:
            time_index = 0
            value_index = 1
            self.data_type = "scalar"
        elif number_of_entries == 6:
            # Local scalar value probed at a point:
            time_index = 1
            value_index = 5
            self.data_type = "scalar"
        elif number_of_entries == 8:
            # Local vector value probed at a point:
            time_index = 1
            value_index = [5, 6, 7]
            self.data_type = "vector"
        elif number_of_entries == 14:
            # Local tensor value probed at a point:
            time_index = 1
            value_index = [[5, 6, 7], [8, 9, 10], [11, 12, 13]]
            self.data_type = "tensor"
        else:
            raise ValueError(f"{filePath} contains an unexpected type of data.")

        # Pack entries for each line:
        entries = [
            entries[i : i + number_of_entries]
            for i in range(0, len(entries), number_of_entries)
        ]

        for entry in entries:
            if self.data_type == "scalar":
                self.time_values.append(float(entry[time_index]))
                self.values.append(float(entry[value_index]))
            elif self.data_type == "vector":
                self.time_values.append(float(entry[time_index]))
                self.values.append(
                    (
                        float(entry[value_index[0]]),
                        float(entry[value_index[1]]),
                        float(entry[value_index[2]]),
                    )
                )
            elif self.data_type == "tensor":
                self.time_values.append(float(entry[time_index]))
                self.values.append(
                    [
                        [
                            float(entry[value_index[0][0]]),
                            float(entry[value_index[0][1]]),
                            float(entry[value_index[0][2]]),
                        ],
                        [
                            float(entry[value_index[1][0]]),
                            float(entry[value_index[1][1]]),
                            float(entry[value_index[1][2]]),
                        ],
                        [
                            float(entry[value_index[2][0]]),
                            float(entry[value_index[2][1]]),
                            float(entry[value_index[2][2]]),
                        ],
                    ]
                )

    def get_equivalent_scalar_values(self):
        """
        Returns the same scalar if self.data_type is scalar.
        Returns the magnitude of the vectors if self.data_type is vector.
        Returns the von misses equivalents of the tensors if self.data_type is tensor.
        """

        if self.data_type == "scalar":
            return self.values
        elif self.data_type == "vector":
            magnitudes = [
                math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
                for v in self.values
            ]
            return magnitudes
        elif self.data_type == "tensor":
            von_misses_equivalents = [
                math.sqrt(
                    0.5
                    * (
                        (v[0][0] - v[1][1]) ** 2
                        + (v[1][1] - v[2][2]) ** 2
                        + (v[2][2] - v[0][0]) ** 2
                        + 6
                        * (
                            ((v[0][1] + v[1][0]) / 2) ** 2
                            + ((v[1][2] + v[2][1]) / 2) ** 2
                            + ((v[0][2] + v[2][0]) / 2) ** 2
                        )
                    )
                )
                for v in self.values
            ]
            return von_misses_equivalents
        else:
            raise RuntimeError("Data type not recognized.")
