#!/bin/bash

RESET="\033[0m"

# Standard 16 ANSI Colors
echo "=== Standard 16 ANSI Colors ==="
echo ""
echo "Foreground colors (normal):"
for i in {30..37}; do
    printf "\033[${i}m %3s $RESET" "$i"
done
echo ""

echo "Foreground colors (bright):"
for i in {90..97}; do
    printf "\033[${i}m %3s $RESET" "$i"
done
echo ""
echo ""

echo "Background colors (normal):"
for i in {40..47}; do
    printf "\033[${i}m %3s $RESET" "$i"
done
echo ""

echo "Background colors (bright):"
for i in {100..107}; do
    printf "\033[${i}m %4s $RESET" "$i"
done
echo ""
echo ""

# Text Styles
echo "=== Text Styles ==="
echo ""
printf "\033[1mBold$RESET  "
printf "\033[2mDim$RESET  "
printf "\033[3mItalic$RESET  "
printf "\033[4mUnderline$RESET  "
printf "\033[7mInverse$RESET  "
printf "\033[9mStrikethrough$RESET"
echo ""
echo ""

# Combined Styles
echo "=== Combined Styles ==="
echo ""
printf "\033[1;31mBold Red$RESET  "
printf "\033[1;4;32mBold Underline Green$RESET  "
printf "\033[3;33mItalic Yellow$RESET  "
printf "\033[1;3;4;35mBold Italic Underline Magenta$RESET"
echo ""
echo ""

# 256 Color Palette
echo "=== 256 Color Palette ==="
echo ""

echo "Standard colors (0-15):"
for i in {0..15}; do
    printf "\033[48;5;${i}m %3s $RESET" "$i"
done
echo ""
echo ""

echo "216 colors (16-231):"
for i in {16..231}; do
    printf "\033[48;5;${i}m  $RESET"
    if (( (i - 15) % 36 == 0 )); then
        echo ""
    fi
done
echo ""

echo "Grayscale (232-255):"
for i in {232..255}; do
    printf "\033[48;5;${i}m %3s $RESET" "$i"
done
echo ""
echo ""

# True Color (24-bit RGB)
echo "=== True Color (24-bit RGB) ==="
echo ""

echo "RGB Gradient (Red -> Green -> Blue):"
for i in {0..77}; do
    if [ $i -lt 26 ]; then
        r=$((255 - i * 10))
        g=$((i * 10))
        b=0
    elif [ $i -lt 52 ]; then
        r=0
        g=$((255 - (i - 26) * 10))
        b=$(((i - 26) * 10))
    else
        r=$(((i - 52) * 10))
        g=0
        b=$((255 - (i - 52) * 10))
    fi
    printf "\033[48;2;${r};${g};${b}m $RESET"
done
echo ""
echo ""

echo "Sample RGB Colors:"
printf "\033[38;2;255;105;180mHot Pink$RESET  "
printf "\033[38;2;0;255;255mCyan$RESET  "
printf "\033[38;2;255;165;0mOrange$RESET  "
printf "\033[38;2;138;43;226mBlue Violet$RESET  "
printf "\033[48;2;220;20;60m\033[38;2;255;255;255m Crimson BG $RESET"
echo ""
echo ""

# Unicode Test
echo "=== Unicode Test ==="
echo ""
echo "Box Drawing: ┌─────┐"
echo "             │ Box │"
echo "             └─────┘"
echo ""
echo "Arrows: ← ↑ → ↓ ↔ ↕"
echo "Math: ∑ ∏ ∫ ∂ √ ∞ ≠ ≤ ≥"
echo "Emoji: 👻 🖥️ ⌨️ 🚀 ✨"
echo "Languages: 你好 こんにちは مرحبا שלום"
echo ""

