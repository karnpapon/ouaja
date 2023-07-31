from app.input import Input
from app.main import main

if __name__ == "__main__":
    inp = Input()
    inp.start()
    main()
    inp.join()
