import calliopeLibraries from "../calliope/libraries.json";
import calliopeRawLibraries from "../calliope/libraries.raw.json";
import microbitLibraries from "../microbit/libraries.json";
import microbitRawLibraries from "../microbit/libraries.raw.json";

export type Device = "calliope" | "microbit";
export type LibraryMap = Record<string, string>;

const minified: Record<Device, LibraryMap> = {
  calliope: calliopeLibraries,
  microbit: microbitLibraries,
};

const raw: Record<Device, LibraryMap> = {
  calliope: calliopeRawLibraries,
  microbit: microbitRawLibraries,
};

const DEVICES = Object.keys(minified) as Device[];

// `device` is typed as Device, but plain-JS callers can pass anything at runtime,
// so this turns an undefined-property TypeError into a message naming the valid options.
function assertDevice(device: Device): void {
  if (!(device in minified)) {
    throw new Error(
      `Unknown device: ${device}. Valid devices are: ${DEVICES.join(", ")}`,
    );
  }
}

/** Names of all supported devices. */
export function listDevices(): Device[] {
  return [...DEVICES];
}

/** Names of all libraries available for a device. */
export function listLibraries(device: Device): string[] {
  assertDevice(device);
  return Object.keys(minified[device]);
}

/** Minified source of a single library, keyed by device and library name (without .py extension). */
export function getLibrary(device: Device, name: string): string {
  assertDevice(device);
  const source = minified[device][name];
  if (source === undefined) {
    throw new Error(
      `Unknown ${device} library: ${name}. Valid libraries are: ${listLibraries(device).join(", ")}`,
    );
  }
  return source;
}

/** Original, unminified source of a single library. */
export function getRawLibrary(device: Device, name: string): string {
  assertDevice(device);
  const source = raw[device][name];
  if (source === undefined) {
    throw new Error(
      `Unknown ${device} raw library: ${name}. Valid libraries are: ${listLibraries(device).join(", ")}`,
    );
  }
  return source;
}

export {
  calliopeLibraries,
  calliopeRawLibraries,
  microbitLibraries,
  microbitRawLibraries,
};
