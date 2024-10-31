let p5Obj;
let brushColor = '#000'; // 기본 브러시 색상
let brushSize = 2; // 기본 브러시 크기
let selectedTool = 'brush'; // 기본 도구는 브러시

const s = p => {
    p.setup = () => {
        // p.createCanvas(890, 700);
        p.createCanvas(getCanvasWidth(), getCanvasHeight());
        p.background(255);

        // 캔버스에 스타일 추가
        const canvasElement = document.getElementById('defaultCanvas0');
        canvasElement.style.border = '5px solid #F7E0DF'; // 핑크색 테두리
        canvasElement.style.borderRadius = '10px'; // 둥근 테두리
        canvasElement.style.boxShadow = '0 0 15px rgba(247, 224, 223, 0.5)'; // 그림자 효과

        document.getElementById('clear').onclick = () => {
            p.background(255);
        };
    }

    p.draw = () => {
        if (p.mouseIsPressed) {
            if (selectedTool === 'eraser') {
                p.stroke('#FFFFFF'); // 지우개 모드에서는 항상 흰색으로 설정
            } else {
                p.stroke(brushColor); // 브러시 모드에서는 현재 색상 설정
            }
            p.strokeWeight(brushSize); // 브러시 크기
            p.line(p.mouseX, p.mouseY, p.pmouseX, p.pmouseY);
        }
    }

    p.windowResized = () => {
        p.resizeCanvas(getCanvasWidth(), getCanvasHeight());
        p.background(255); // 윈도우 크기가 변경될 때 캔버스를 흰색으로 초기화
    };
};

function onLoad() {
    p5Obj = new p5(s, 'operation-canvas');
}

// 새로운 슬라이더(range-input) 값 업데이트 및 브러시 크기 조절
let customSlider = document.getElementById('custom-slider');
let rangeValue = document.querySelector('.range-input .value div');

// 슬라이더 최소, 최대, 스텝 값 가져오기
let start = parseFloat(customSlider.min);
let end = parseFloat(customSlider.max);
let step = parseFloat(customSlider.step);

// 슬라이더 값 초기화 (0에서 100까지 10씩 증가하는 값 표시)
for (let i = start; i <= end; i += step) {
    rangeValue.innerHTML += '<div>' + i + '</div>';
}

// 슬라이더 값 변화 시 값 표시 업데이트 및 브러시 크기 업데이트
customSlider.addEventListener('input', function () {
    let top = parseFloat(customSlider.value) / step * -40;
    rangeValue.style.marginTop = top + 'px';

    // 슬라이더 값에 따라 브러시 크기 업데이트
    if (parseInt(customSlider.value) === 0) {
        brushSize = 3;
    } else {
        brushSize = parseInt(customSlider.value) / 3; // 슬라이더 값에 따라 브러시 크기 업데이트
    }
});

// 색상 선택기 및 도구 선택 등의 기존 이벤트 유지
document.querySelectorAll('.colors .option').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelector('.colors .selected').classList.remove('selected');
        btn.classList.add('selected');
        brushColor = window.getComputedStyle(btn).getPropertyValue('background-color');
        if (selectedTool !== 'eraser') {
            p5Obj.stroke(brushColor); // 브러시 색상 업데이트
        }
    });
});

document.getElementById('color-picker').addEventListener('input', (event) => {
    brushColor = event.target.value;
    if (selectedTool !== 'eraser') {
        p5Obj.stroke(brushColor); // 브러시 색상 업데이트
    }
    document.querySelector('.colors .selected').style.backgroundColor = brushColor; // 색상 버튼 업데이트
});

document.querySelectorAll('.tools-board .tool').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelector('.tools-board .active').classList.remove('active');
        btn.classList.add('active');
        selectedTool = btn.id;
        if (selectedTool === 'eraser') {
            p5Obj.stroke('#FFFFFF'); // 지우개 모드에서는 항상 흰색으로 설정
        } else {
            p5Obj.stroke(brushColor); // 브러시 모드에서는 현재 색상 설정
        }
    });
});

function predict() {
    const canvas = document.getElementById('defaultCanvas0');
    const base64Canvas = canvas.toDataURL('image/png').replace('data:image/png;base64,', '');

    const data = {
        operation: base64Canvas,
    };

    $.ajax({
        url: '/predict',
        type: 'POST',
        data: data,
    }).done(function (data) {
        let result = JSON.parse(data);
        $('#operation-container').html(`${result.operation} = ${result.solution}`);
        $('#explanation-container').html(result.explanation);
    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
        console.log(XMLHttpRequest);
        alert('Error occurred while processing.');
    });
}


// 캔버스 크기 설정
function getCanvasWidth() {
    const width = window.innerWidth;

    // iPad Mini는 일반적으로 768px 이하
    if (width < 600) {
        return width * 0.34; // 작은 화면 (600px 미만)에서는 화면 너비의 30%로 설정
    } 
    // iPad Mini (768px 이하)
    else if (width >= 600 && width < 768) {
        return width * 0.5; // iPad Mini 크기일 때는 화면 너비의 50%
    }
    // iPad 기본 모델 (768px ~ 834px)
    else if (width >= 768 && width < 834) {
        return width * 0.6; // iPad 기본일 때는 화면 너비의 60%
    } 
    // iPad Pro 11인치 (834px ~ 1024px)
    else if (width >= 834 && width < 1024) {
        return width * 0.623; // iPad Pro 11인치에서는 화면 너비의 65%
    }
    // iPad Pro 12.9인치 (1024px ~ 1366px)
    else if (width >= 1024 && width < 1200) {
        return width * 0.635; // iPad Pro 12.9인치에서는 화면 너비의 70%

    }
    // 큰 화면 (1366px 이상)
    else {
        return 725;  // 큰 화면에서는 고정된 725px로 설정
    }
}


function getCanvasHeight() {
    return 350; // 기본 높이
}

function windowResized() {
    resizeCanvas(getCanvasWidth(), getCanvasHeight());
    console.log(getCanvasWidth());
}

// 추가 확인버튼 
function confirmCalculation() {
    const canvas = document.getElementById('defaultCanvas0');
    const base64Canvas = canvas.toDataURL('image/png').replace('data:image/png;base64,', '');

    const data = {
        operation: base64Canvas,
    };

    $.ajax({
        url: '/predict',
        type: 'POST',
        data: data,
    }).done(function (data) {
        let result = JSON.parse(data);
        // 연산식과 함께 새로운 문구 추가
        $('#operation-container').html(`${result.operation} <span style="font-weight: bold;">작성하신 계산식이 올바른가요? 올바르다면 계산 시작하기를 눌러 풀이를 확인하세요.</span>`);
        $('#explanation-container').html(''); // 풀이 방법 숨김
    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
        console.log(XMLHttpRequest);
        alert('Error occurred while processing.');
    });
}



