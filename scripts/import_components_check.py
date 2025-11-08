import sys
from pathlib import Path
proj = Path(__file__).parent.parent.resolve()
if str(proj) not in sys.path:
    sys.path.insert(0, str(proj))

import components
print('components imported OK')
print('exports sample:', components.__all__[:10])
