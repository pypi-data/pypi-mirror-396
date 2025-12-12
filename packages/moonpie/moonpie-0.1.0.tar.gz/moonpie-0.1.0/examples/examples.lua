-- MoonPie Lua Interpreter Examples

print("=== Fibonacci Sequence ===")
function fibonacci(n)
    if n <= 1 then
        return n
    end
    return fibonacci(n - 1) + fibonacci(n - 2)
end

for i = 0, 10 do
    print("fib(" .. tostring(i) .. ") = " .. tostring(fibonacci(i)))
end

print("\n=== Table Manipulation ===")
local fruits = {"apple", "banana", "cherry", "date"}
for i = 1, #fruits do
    print(i .. ": " .. fruits[i])
end

print("\n=== Higher-Order Functions ===")
function map(arr, fn)
    local result = {}
    for i = 1, #arr do
        result[i] = fn(arr[i])
    end
    return result
end

function double(x)
    return x * 2
end

local numbers = {1, 2, 3, 4, 5}
local doubled = map(numbers, double)
for i = 1, #doubled do
    print(doubled[i])
end

print("\n=== Closures ===")
function makeCounter()
    local count = 0
    return function()
        count = count + 1
        return count
    end
end

local counter = makeCounter()
print(counter())
print(counter())
print(counter())

print("\n=== Math Library ===")
print("pi = " .. tostring(math.pi))
print("sqrt(16) = " .. tostring(math.sqrt(16)))
print("max(5, 10, 3) = " .. tostring(math.max(5, 10, 3)))
print("min(5, 10, 3) = " .. tostring(math.min(5, 10, 3)))

print("\n=== String Library ===")
local text = "Hello World"
print("Original: " .. text)
print("Upper: " .. string.upper(text))
print("Lower: " .. string.lower(text))
print("Length: " .. tostring(string.len(text)))
print("Substring (1,5): " .. string.sub(text, 1, 5))

print("\n=== Nested Functions ===")
function outer(x)
    local function inner(y)
        return x + y
    end
    return inner
end

local add5 = outer(5)
print(add5(3))
print(add5(7))

print("\n=== Complex Table ===")
local person = {
    name = "Alice",
    age = 30,
    address = {
        city = "New York",
        country = "USA"
    },
    hobbies = {"reading", "coding", "gaming"}
}

print("Name: " .. person.name)
print("Age: " .. tostring(person.age))
print("City: " .. person.address.city)
print("First hobby: " .. person.hobbies[1])

print("\n=== Boolean Logic ===")
local function check(value)
    if not value then
        return "None"
    elseif value > 10 then
        return "Large"
    elseif value > 5 then
        return "Medium"
    else
        return "Small"
    end
end

print(check(15))
print(check(8))
print(check(3))
print(check(nil))
