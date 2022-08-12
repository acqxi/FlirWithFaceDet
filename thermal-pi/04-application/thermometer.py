#!/usr/bin/python3

import argparse
import configparser
import os
import queue
import sys
import threading
import time

import cv2
import imutils
import numpy as np
from pylepton.Lepton3 import Lepton3


# bufferless VideoCapture
class VideoCapture:

    def __init__( self, name ):
        self.cap = cv2.VideoCapture( name )
        self.q = queue.Queue()
        t = threading.Thread( target=self._reader )
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader( self ):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put( frame )

    def read( self ):
        return self.q.get()


class HiddenPrints:

    def __enter__( self ):
        self._original_stdout = sys.stdout
        sys.stdout = open( os.devnull, 'w' )

    def __exit__( self, exc_type, exc_val, exc_tb ):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def path(string):
    if os.path.exists(string):
        return string
    else:
        sys.exit(f'File not found: {string}')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument( '--show', '-s', help="show real-time pic be taken from device", type=bool, default=True )
    parser.add_argument( '--confidence','-cf', help="confidence df: .5", type=int, default=0.5 )
    parser.add_argument( '--fontscale', '-fs', help="font scale df: 1", type=int, default=1 )
    parser.add_argument( '--screenscale', '-ss', help="screen scale df: 1", type=int, default=1 )
    parser.add_argument( '--fontthick','-ft', help="font thickness df: 2", type=int, default=3 )
    parser.add_argument( '--adjust', '-ad', help="adjust temp + ?", type=float, default=1.5 )
    parser.add_argument( '--modeldeploy', '-md', help="model's deploy text file df: deploy.prototxt.txt", type=path, default='deploy.prototxt.txt' )
    parser.add_argument( '--caffemodel', '-cm', help="caffe model file df: res10_300x300_ssd_iter_140000.caffemodel)", type=path, default='res10_300x300_ssd_iter_140000.caffemodel' )

    argsin = sys.argv[ 1: ]
    return parser.parse_args( argsin )


def rotate( image, angle, center=None, scale=1.0 ):
    # 获取图像尺寸
    ( h, w ) = image.shape[ :2 ]

    # 若未指定旋转中心，则将图像中心设为旋转中心
    if center is None:
        center = ( w / 2, h / 2 )

    # 执行旋转
    M = cv2.getRotationMatrix2D( center, angle, scale )
    rotated = cv2.warpAffine( image, M, ( w, h ) )

    # 返回旋转后的图像
    return rotated


net = cv2.dnn.readNetFromCaffe( 'deploy.prototxt.txt', 'res10_300x300_ssd_iter_140000.caffemodel' )


def main():
    print( 'start' )
    config = configparser.ConfigParser()
    config.read( '../fusion.conf' )
    visible_win_w = int( config.get( 'visible', 'win_w' ) )
    cstartX = int( config.get( 'stereo', 'startX' ) )
    cstartY = int( config.get( 'stereo', 'startY' ) )
    cendX = int( config.get( 'stereo', 'endX' ) )
    cendY = int( config.get( 'stereo', 'endY' ) )

    cap = VideoCapture( 0 )
    # cap.set( cv2.CAP_PROP_FPS, 25 )
    # cap.set( cv2.CAP_PROP_BUFFERSIZE, 0 )
    args = get_args()
    showing = args.show

    # try:
    with Lepton3() as leptonCap:
        while True:
            time_s = time.time()
            with HiddenPrints():
                a, _ = leptonCap.capture()
                raw_a = a.copy()
            cv2.normalize( a, a, 0, 65535, cv2.NORM_MINMAX )
            np.right_shift( a, 8, a )
            _a = np.asarray( a, np.uint8 )
            _a_rgb = cv2.applyColorMap( _a, cv2.COLORMAP_HOT )

            img2 = cap.read()
            if img2.shape[ 1 ] != visible_win_w:
                img2 = imutils.resize( img2, visible_win_w )
            crop_img2 = img2[ cstartY:cendY, cstartX:cendX ]

            frame = crop_img2

            # print( f"{img2.shape}, {crop_img2.shape}, {frame.shape}" )

            frame = rotate( frame, 0 )
            # grab the frame dimensions and convert it to a blob
            ( h, w ) = frame.shape[ :2 ]

            blob = cv2.dnn.blobFromImage( cv2.resize( frame, ( 300, 300 ) ), 1.0, ( 300, 300 ), ( 104.0, 177.0, 123.0 ) )

            net.setInput( blob )
            detections = net.forward()

            for i in range( 0, detections.shape[ 2 ] ):
                # extract the confidence (i.e., probability) associated with the
                # prediction
                confidence = detections[ 0, 0, i, 2 ]

                # filter out weak detections by ensuring the `confidence` is
                # greater than the minimum confidence
                if confidence < args.confidence:
                    continue

                # compute the (x, y)-coordinates of the bounding box for the
                # object
                box = detections[ 0, 0, i, 3:7 ] * np.array( [ w, h, w, h ] )
                ( startX, startY, endX, endY ) = box.astype( "int" )

                # draw the bounding box of the face along with the associated
                # probability
                # text = "{:.2f}%".format(confidence * 100)
                x = startX
                y1 = int( .1 * startY + .9 * endY )
                y2 = int( .3 * startY + .7 * endY )
                ax = startX * ( 160 ) // abs( cstartX - cendX )
                aex = endX * ( 160 ) // abs( cstartX - cendX )
                ay = startY * ( 120 ) // abs( cstartY - cendY )
                aey = endY * ( 120 ) // abs( cstartY - cendY )
                try:
                    temp_face = ( np.nanmax( raw_a[ ax:aex, ay:aey ] ) - 27315 ) / 100 + args.adjust
                except Exception as e:
                    print( 'continue with error : ', e )
                cv2.rectangle( _a_rgb, ( ax, ay ), ( aex, aey ), ( 0, 255, 0 ), 2 )
                cv2.rectangle( frame, ( startX, startY ), ( endX, endY ), ( 0, 0, 255 ), 2 )
                # print( temp_face )

                try:
                    # print((np.max(temp_face.ravel()) - 27315) / 100.0)
                    # temp_max = (np.max(temp_face.ravel()) - 27315) / 100.0
                    # cv2.putText(frame, str(temp_max), (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                    cv2.putText(
                        frame, f"Temp: {temp_face:.1f}", ( x, y2 ), cv2.FONT_HERSHEY_SIMPLEX, args.fontscale, ( 0, 0, 255 ),
                        args.fontthick )
                    cv2.putText(
                        frame, f"CF: {int(100*confidence)}%", ( x, y1 ), cv2.FONT_HERSHEY_SIMPLEX, args.fontscale,
                        ( 0, 0, 255 ), args.fontthick )
                except Exception as error:
                    print( error )
                    pass  #

            if showing:
                img1 = cv2.resize( _a_rgb, ( 320, 240 ), interpolation=cv2.INTER_CUBIC )

                crop_img2 = cv2.resize( frame, ( 320, 240 ) )

                horizontal = np.hstack( ( img1, crop_img2 ) )
                cv2.imshow( "dual_camera", horizontal )

            if cv2.waitKey( 1 ) & 0xFF == ord( "q" ):
                showing = False
                cv2.destroyAllWindows()

            # if cv2.waitKey( 1 ) & 0xFF == ord( "r" ):
            #     recording = True

            # if recording:
            #     cv2.imwrite( os.path.join( dir_path, f'{frame_num:05}.png' ), _a, [ cv2.IMWRITE_PNG_COMPRESSION, 0 ] )
            #     cv2.imwrite(
            #         os.path.join( dir_path, f'{frame_num:05}.jpg' ), cv2.resize( crop_img2, ( 512, 384 ) ),
            #         [ cv2.IMWRITE_JPEG_QUALITY, 90 ] )
            #     frame_num += 1

            cost = 1 / ( time.time() - time_s )
            # time.sleep( .1 )
            print( f"\rFPS :{cost:.2f}", end='' )
            # break

    # except Exception as e:
    #     print( e )

    # finally:
    #     cap.release()


if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()
