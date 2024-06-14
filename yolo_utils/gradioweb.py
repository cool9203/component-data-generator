import PIL.Image as Image
import gradio as gr

from ultralytics import ASSETS, YOLO

#model = YOLO("./custom_data/runs/detect/train2/weights/best.pt")
#model = YOLO("./custom_data_v3/runs/detect/train5/weights/best.pt")
#model = YOLO("./custom_data_v3/runs/detect/train6/weights/best.pt")
model = YOLO("./custom_data/runs/detect/train/weights/best.pt ")


def predict_image(img, conf_threshold, iou_threshold):
    """Predicts and plots labeled objects in an image using YOLOv8 model with adjustable confidence and IOU thresholds."""
    results = model.predict(
        source=img,
        conf=conf_threshold,
        iou=iou_threshold,
        show_labels=True,
        show_conf=True,
        imgsz=640,
        line_width=1,
    )

    for r in results:
        print(type(r))
        im_array = r.plot(conf=True,labels=True)
        im = Image.fromarray(im_array[..., ::-1])

    return im


iface = gr.Interface(
    fn=predict_image,
    inputs=[
        gr.Image(type="pil", label="Upload Image"),
        gr.Slider(minimum=0, maximum=1, value=0.25, label="Confidence threshold"),
        gr.Slider(minimum=0, maximum=1, value=0.45, label="IoU threshold")
    ],
    outputs=gr.Image(type="pil", label="Result"),
    title="Ultralytics Gradio",
    description="Upload images for inference. The Ultralytics YOLOv8n model is used by default.",
    examples=[
        [ASSETS / "bus.jpg", 0.25, 0.45],
        [ASSETS / "zidane.jpg", 0.25, 0.45],
    ]
)

if __name__ == '__main__':
    iface.launch(server_port=30300,server_name='0.0.0.0')
