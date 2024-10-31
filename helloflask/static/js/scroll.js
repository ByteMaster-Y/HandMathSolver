const contents = document.querySelectorAll('.content');

appear();

function appear() {
  const triggerBottom = (window.innerHeight / 5) * 4;

  if(contents){
     contents.forEach((content) => {
    const contentTop = content.getBoundingClientRect().top;

    if (contentTop < triggerBottom) {
      content.classList.add("show");
    } else {
      content.classList.remove("show");
    }
  });
  }
}

window.addEventListener("scroll", appear);