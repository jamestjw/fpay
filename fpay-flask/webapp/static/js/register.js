var video = document.querySelector("#videoElement");
var imageCapture;
if (navigator.mediaDevices.getUserMedia) {
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        const track = stream.getVideoTracks()[0];
        imageCapture = new ImageCapture(track);
    })
    .catch(error => {
        console.log(error);
    });
}

function onGrabFrameButtonClick() {
    imageCapture.takePhoto()
    .then(blob => {
        grabBlob = blob;
        return createImageBitmap(blob)
    })
    .then(imageBitmap => {
        const canvas = document.querySelector('#grabFrameCanvas');
        document.querySelector('#webcamgrab').style.display = "block";
        const webcam = document.querySelector('#webcamvideo');
        webcam.style.display = "none";
        drawCanvas(canvas, imageBitmap);
    })
    .catch(error => console.log(error));
}

function onTakePhotoButtonClick() {
    imageCapture.takePhoto()
    .then(blob => {
        var form = new FormData();
        form.append("image_blob", blob, 'lolblob');
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/identify');
        xhr.onreadystatechange = function() { // Call a function when the state changes.
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                response = JSON.parse(xhr.response)
                name = response['name']
            if (name ==undefined || name ==='undefined'){
                    document.querySelector('#output').innerText = 'Unable to find match. Kindly register with us before trying again.'
                } else {
                    document.querySelector('#output').innerText = name
                }
            }
        }
        xhr.send(form)
    })
    .catch(error => console.log(error));
}

function drawCanvas(canvas, img) {
canvas.width = getComputedStyle(canvas).width.split('px')[0];
canvas.height = getComputedStyle(canvas).height.split('px')[0];
let ratio  = Math.min(canvas.width / img.width, canvas.height / img.height);
let x = (canvas.width - img.width * ratio) / 2;
let y = (canvas.height - img.height * ratio) / 2;
canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
canvas.getContext('2d').drawImage(img, 0, 0, img.width, img.height,
    x, y, img.width * ratio, img.height * ratio);
}

function stop(e) {
    // navigator.mediaDevices.getUserMedia({ video: true })
    // .then(stream => {
    //     console.log('hu')
    //     video.srcObject = stream;
    //     const track = stream.getVideoTracks()[0];
    //     imageCapture = new ImageCapture(track);
    // })
    // .catch(error => {
    //     console.log(error);
    // });
video.srcObject = null;
}


$(function() // execute once the DOM has loaded
{
  var a = document.forms[0]["name"]
  var b = document.forms[0]["phone"]
  // wire up Add Item button click event
  $("form").submit(function(event)
  {
    $.LoadingOverlay("show")
    event.preventDefault(); // cancel default behavior
    if (a.value == null || a.value == "" || b.value == null || b.value == "") {
        alert('Fill in all columns please!')
        $.LoadingOverlay("hide");
    } else if (document.getElementById("image").files.length > 0) {
        $(this).unbind('submit').submit()
    } else if (typeof grabBlob !== 'undefined'){
        var form = new FormData();
        form.append("user_name", a.value);
        form.append("phone", b.value);
        form.append("image", grabBlob, 'image');
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/register');
        xhr.onreadystatechange = function() { // Call a function when the state changes.
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                $.LoadingOverlay("hide");
                window.location.replace(xhr.responseURL);
            }                
        }
        xhr.send(form)        
    } else {
        $.LoadingOverlay("hide");
        alert("You have to either upload a photo or freeze a webcam frame!")
    }
  });
});
