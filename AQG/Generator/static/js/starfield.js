        function addStars(starFieldWidth, starFieldHeight, noOfStars) {
            var starField = document.getElementById('star-field');
            var numberOfStars = noOfStars;

            starField.innerHTML = ''; // Clear existing stars

            for (var i = 0; i < numberOfStars; i++) {
                var star = document.createElement('div');
                star.className = 'star';
                var topOffset = Math.floor((Math.random() * starFieldHeight) + 1);
                var leftOffset = Math.floor((Math.random() * starFieldWidth) + 1);
                star.style.top = topOffset + 'px';
                star.style.left = leftOffset + 'px';
                var size = Math.random() * 2 + 1 + 'px';
                star.style.width = size;
                star.style.height = size;

                var starType = Math.floor(Math.random() * 4);
                switch (starType) {
                    case 0:
                        star.classList.add('white');
                        break;
                    case 1:
                        star.classList.add('yellow');
                        break;
                    case 2:
                        star.classList.add('blue');
                        break;
                    case 3:
                        star.classList.add('red');
                        break;
                }

                starField.appendChild(star);
            }
        }

        function animateStars(starFieldWidth, speed) {
            var starField = document.getElementById('star-field');
            var stars = starField.childNodes;

            function getStarRelativeSpeed(index) {
                if (index % 6 == 0)
                    return 1;
                else if (index % 9 == 0)
                    return 2;
                else if (index % 2 == 0)
                    return -1;
                else
                    return 0;
            }

            setInterval(function() {
                for (var i = 0; i < stars.length; i++) {
                    var star = stars[i];
                    var currentLeft = parseInt(star.style.left, 10);
                    var leftChangeAmount = speed + getStarRelativeSpeed(i);
                    var leftDiff;

                    if (currentLeft - leftChangeAmount < 0) {
                        leftDiff = currentLeft - leftChangeAmount + starFieldWidth;
                    } else {
                        leftDiff = currentLeft - leftChangeAmount;
                    }
                    star.style.left = (leftDiff) + 'px';
                }
            }, 20);
        }

        // Initialize star field
        window.addEventListener('resize', function() {
            addStars(window.innerWidth, window.innerHeight, 150);
        });

        addStars(window.innerWidth, window.innerHeight, 150);
        animateStars(window.innerWidth, 0.5);