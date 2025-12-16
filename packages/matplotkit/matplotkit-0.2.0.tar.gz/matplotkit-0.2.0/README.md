# MatplotKit

MatplotKit is a lightweight Python library designed to enhance Matplotlib with additional features and utilities, making data visualization more convenient and elegant.

## Features

- ✨ **Decorators for Plot Functions**
  - `@with_axes` decorator automatically handles axes creation
  - Simplifies plot function implementation
  - Customizable figure size support

- 📊 **Enhanced Annotations**
  - Easy-to-use diagonal line addition
  - More annotation utilities coming soon

- 📈 **Taylor Diagram Support**
  - Comprehensive implementation of Taylor diagrams
  - Perfect for model evaluation and comparison
  - Customizable styling options

## Installation

Install MatplotKit using pip:

```bash
pip install matplotkit
```

## Quick Start

Here's a simple example of using MatplotKit:

```python
import matplotlib.pyplot as plt
from matplotkit import with_axes, add_diagonal_line

# Using the decorator to automatically handle axes
@with_axes(figsize=(8, 6))
def scatter_plot(x, y, ax=None):
    ax.scatter(x, y)
    # Add a diagonal line with custom style
    add_diagonal_line(ax, color='red', linestyle='--', alpha=0.5)
    return ax

# Your plotting code
x = [1, 2, 3, 4, 5]
y = [1.1, 2.2, 2.9, 4.1, 5.2]
scatter_plot(x, y)
plt.show()
```

## Requirements

- Python >= 3.8.1
- Matplotlib ~3.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Shuang (Twist) Song**
- Email: SongshGeo@gmail.com
- GitHub: [@SongshGeo](https://github.com/SongshGeo)
- Website: https://cv.songshgeo.com/

## Citation

If you use MatplotKit in your research, please cite it as:

```bibtex
@software{matplotkit2024,
  author = {Song, Shuang},
  title = {MatplotKit: Enhanced Matplotlib Utilities},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/SongshGeo/matplotkit}
}
```
