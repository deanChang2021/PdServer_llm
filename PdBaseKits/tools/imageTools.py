import requests
import logging
from PIL import Image

### image_url:图片链接,path:路径 imageName:图片名
def writeImg2Local(imageUrl:str, path:str, imageName:str):
    logging.info(f"write img to local: {imageUrl}, imageName: {imageName}")

    # tmpContentArr = image_url.split("/")
    # tmpImageName = tmpContentArr[len(tmpContentArr)-1]
    # imageNameArr = tmpImageName.split("?")
    # imageName = imageNameArr[0]

    headers ={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }
    r = requests.get(imageUrl, headers=headers)
    # 下载图片

    # 二进制数据需要用r.content 进行提取
    # 将图片放在‘图库’文件夹下，‘图库’是文件夹的名称，将图片放入该文件夹中，该文件夹与py文件在同一目录下
    fileName = path+ "/" + imageName
    logging.info(f"write img to local fileName: {fileName}")
    f = open(fileName,'wb')
    f.write(r.content)
    f.close()




###
### 图片压缩方法。按固定比例压缩。
###
def compressImg(inputImagePath, outputImagePath, width):
    image = Image.open(inputImagePath)


    tup = image.size
    div = tup[0]/tup[1]

    try:
        newWidth = width
        newHeight = int(round(newWidth/div));

        newImage = image.resize((newWidth,newHeight))
        newImage.save(outputImagePath)
        logging.info("compress image output file path["+outputImagePath+"]")
    except Exception as e:
        return str(e)

    return True



### desc:需要分割的图片的可访问的绝对地址。
### numRows：需分割的行数。numCols：需分割的列数。
def splitImg(image_path:str, numRows:int, numCols:int):
    img = Image.open(image_path)
    width, height = img.size
    row_height = height // numRows
    col_width = width // numCols

    oringleFIleName = image_path.split(".png")[0]
    print("oringleFIleName:"+oringleFIleName)
    logging.info("分割图片: width["+str(width)+"],height["+str(height)+"]")

    images = []
    idx = 1
    for row in range(numRows):
        for col in range(numCols):
            left = col * col_width
            top = row * row_height
            right = left + col_width
            bottom = top + row_height
            crop_img = img.crop((left, top, right, bottom))

            filename = oringleFIleName+"-"+str(idx)+".png"
            crop_img.save(filename)
            idx+=1

            images.append(filename)

    return images
