from PIL import Image, ImageDraw, ImageFont

def create_image(filename, color, size=(50, 50), text=None):
    image = Image.new('RGB', size, color=color)
    if text:
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, fill="white", font=font)
    image.save(filename)

def create_water_image(filename, size=(50, 50)):
    image = Image.new('RGB', size, 'blue')
    draw = ImageDraw.Draw(image)
    for i in range(5):
        draw.arc([(10 * i, 0), (10 * (i + 1), size[1])], 0, 180, fill='lightblue', width=3)
    image.save(filename)

def create_ship_image(filename, size=(50, 50)):
    image = Image.new('RGB', size, 'gray')
    draw = ImageDraw.Draw(image)
    draw.rectangle([5, 15, 45, 35], fill='darkgray')
    draw.rectangle([15, 5, 35, 15], fill='darkgray')
    image.save(filename)

def create_hit_image(filename, size=(50, 50)):
    image = Image.new('RGB', size, 'red')
    draw = ImageDraw.Draw(image)
    draw.line([(10, 10), (40, 40)], fill='white', width=5)
    draw.line([(10, 40), (40, 10)], fill='white', width=5)
    image.save(filename)

def create_miss_image(filename, size=(50, 50)):
    image = Image.new('RGB', size, 'blue')
    draw = ImageDraw.Draw(image)
    draw.ellipse([(15, 15), (35, 35)], outline='white', width=5)
    image.save(filename)

def create_explosion_gif(filename, size=(50, 50), frames=5):
    images = []
    for i in range(frames):
        image = Image.new('RGB', size, 'orange')
        draw = ImageDraw.Draw(image)
        draw.ellipse([(10, 10), (40, 40)], fill='red')
        draw.line([(25, 0), (25, 50)], fill='yellow', width=5)
        draw.line([(0, 25), (50, 25)], fill='yellow', width=5)
        images.append(image)
    images[0].save(filename, save_all=True, append_images=images[1:], loop=0, duration=100)

create_water_image('water.png')
create_ship_image('ship.png')
create_hit_image('hit.png')
create_miss_image('miss.png')
create_explosion_gif('explosion.gif')

print("Images created successfully.")
