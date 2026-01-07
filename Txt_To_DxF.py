import sys
import os
import pandas as pd
import shapefile # pyshp 라이브러리
# pip install pandas pyshp 꼭하기!!!
# 1. 함수로 묶기

def convert_gps_to_shp(input_path):
    # -1. 경로 정리 (따옴표 제거 등)
    # input_path가 문자열인지 확인 후 처리
    input_path = str(input_path).strip().strip('"').strip("'")

    if not os.path.exists(input_path):
        print(f"\n !!오류!! 파일을 찾을 수 없습니다: {input_path}")
        return

    # -2. 출력파일 경로 설정
    dir_name = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_name = f"{base_name}_For_arcgis" 
    # 확장자는 writer가 알아서 붙임, 경로 결합
    output_path = os.path.join(dir_name, output_name)

    print(f"\n !작업 시작! : {base_name}.txt -> {output_name}.shp 로 변환중 \n")

    # -3. GPS 텍스트 파일 읽기
    try:
        # 'input_path' 따옴표 제거 -> 변수 input_path 사용
        df = pd.read_csv(input_path, header=None, names=['lat', 'lon'], skipinitialspace=True)
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return

    print(f"파일 읽기 완료: {len(df)}개의 좌표 데이터 확인됨.")

    # -4. Shapefile (DBF 포함) 생성기 설정
    w = shapefile.Writer(output_path, shapeType=shapefile.POINT)

    # 3. DBF 필드(컬럼) 만들기
    w.field('ID', 'N', 10, 0)      # 순번
    w.field('LAT', 'N', 20, 8)     # 위도
    w.field('LON', 'N', 20, 8)     # 경도

    # -5. 데이터 변환 및 쓰기
    print("변환 중입니다... (데이터 양에 따라 시간이 걸릴 수 있습니다)")
    
    for index, row in df.iterrows():
        try:
            lat = float(row['lat'])
            lon = float(row['lon'])

            # 1) 지오메트리 생성 (GIS: 경도 lon, 위도 lat 순서)
            w.point(lon, lat)

            # 2) DBF 속성값 입력
            w.record(index + 1, lat, lon)
            
        except ValueError:
            print(f"경고: 잘못된 좌표 데이터 건너뜀 (행 {index + 1}): {row}")
            continue

    w.close()

    # -6. PRJ 파일 생성 (좌표계 정보-Type_WGS84)
    wgs84_wkt = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
    
    # shapefile.Writer는 확장자를 자동으로 붙이지만 open은 안 붙이므로 .prj 명시
    prj_path = os.path.join(dir_name, output_name + ".prj")
    with open(prj_path, "w") as prj:
        prj.write(wgs84_wkt)

    print("-" * 40)
    print(f" !!변환 완료!!")
    print(f" 저장 위치: {dir_name}")
    print(f" 생성 파일: {output_name}.shp (및 .dbf, .shx, .prj)")
    print(" ArcGIS에서 .shp 파일을 바로 열어서 사용하세요. ")
    print("-" * 40)

# 2. 파일 드래그로 넣고 싶어서 추가 부분
if __name__ == "__main__":
    # 인자가 있을 때 (파일 드래그 앤 드롭으로 실행 시)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        convert_gps_to_shp(file_path) # 함수 호출 괄호 추가
        # 바로 꺼지지 않게 하려면 아래 주석 해제
        # input("종료하려면 엔터 키를 누르세요...")

    # 그냥 실행했을 때
    else:
        print("사용법: 변환할 GPS 텍스트 파일을 이 스크립트에 드래그 앤 드롭하여 실행하세요.")
        file_path = input("파일경로 : ")
        convert_gps_to_shp(file_path)